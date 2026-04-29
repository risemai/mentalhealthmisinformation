"""
fetcher.py — YouTube Data API v3 helpers
"""

import re
import requests
import pandas as pd



#  Video ID extraction


def extract_video_id(url_or_id: str) -> str | None:
    """Return an 11-char YouTube video ID, or None if not found."""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        m = re.search(pattern, url_or_id)
        if m:
            return m.group(1)
    return None



#  Duration parser


def _parse_duration(iso: str) -> str:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "PT0S")
    if not m:
        return "0:00"
    h, mn, s = (int(x or 0) for x in m.groups())
    return f"{h}:{mn:02d}:{s:02d}" if h else f"{mn}:{s:02d}"



#  Metadata


def fetch_video_metadata(video_id: str, api_key: str) -> tuple[dict | None, str | None]:
    """Return (meta_dict, error_string).  One will be None."""
    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "id": video_id,
                "key": api_key,
                "part": "snippet,statistics,contentDetails",
            },
            timeout=15,
        )
        data = resp.json()
        if "error" in data:
            return None, data["error"].get("message", "YouTube API error")

        items = data.get("items", [])
        if not items:
            return None, "Video not found — check the ID or URL."

        item = items[0]
        sn = item.get("snippet", {})
        st = item.get("statistics", {})
        cd = item.get("contentDetails", {})

        meta = {
            "title":         sn.get("title", "Unknown"),
            "description":   sn.get("description", ""),
            "channel_title": sn.get("channelTitle", "Unknown"),
            "published_at":  sn.get("publishedAt", "")[:10],
            "tags":          sn.get("tags", []),
            "thumbnail_url": (
                sn.get("thumbnails", {}).get("high", {}).get("url", "")
                or sn.get("thumbnails", {}).get("medium", {}).get("url", "")
            ),
            "view_count":    int(st.get("viewCount", 0)),
            "like_count":    int(st.get("likeCount", 0)),
            "comment_count": int(st.get("commentCount", 0)),
            "duration":      _parse_duration(cd.get("duration", "PT0S")),
        }
        return meta, None

    except requests.exceptions.Timeout:
        return None, "Request timed out. Check your internet connection."
    except Exception as exc:
        return None, str(exc)



#  Transcript


def fetch_transcript(video_id: str) -> tuple[str, str]:
    """Return (text, status_message).

    Supports both youtube_transcript_api < 1.0 (static get_transcript) and
    >= 1.0 (instance-based api.fetch).
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        segments = None

        # New API (>= 1.0.0): class no longer exposes static get_transcript
        if not hasattr(YouTubeTranscriptApi, "get_transcript"):
            api = YouTubeTranscriptApi()
            raw = api.fetch(video_id)
            # Each item is a snippet object; text attr varies by version
            segments = [{"text": getattr(s, "text", "") or s.get("text", "")} for s in raw]
        else:
            # Legacy API (< 1.0.0)
            segments = YouTubeTranscriptApi.get_transcript(video_id)

        text = " ".join(s["text"] for s in (segments or []))
        if not text.strip():
            return "", " Transcript unavailable: empty transcript returned"
        return text, f" Transcript: {len(text.split())} words"

    except Exception as exc:
        short = str(exc)[:120]
        return "", f" Transcript unavailable: {short}"



#  Comments


def fetch_comments(
    video_id: str,
    api_key: str,
    max_comments: int = 150,
) -> tuple[pd.DataFrame, str]:
    """Return (DataFrame, status_message)."""
    rows = []
    next_token = None

    try:
        while len(rows) < max_comments:
            want = min(100, max_comments - len(rows))
            params = {
                "videoId":    video_id,
                "key":        api_key,
                "part":       "snippet",
                "maxResults": want,
                "order":      "relevance",
            }
            if next_token:
                params["pageToken"] = next_token

            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/commentThreads",
                params=params,
                timeout=15,
            )
            data = resp.json()

            if "error" in data:
                msg = data["error"].get("message", "Comment API error")
                break

            for item in data.get("items", []):
                c = item["snippet"]["topLevelComment"]["snippet"]
                rows.append({
                    "author":       c.get("authorDisplayName", ""),
                    "text":         c.get("textDisplay", ""),
                    "likes":        int(c.get("likeCount", 0)),
                    "published_at": c.get("publishedAt", "")[:10],
                })

            next_token = data.get("nextPageToken")
            if not next_token or not data.get("items"):
                break

        if not rows:
            return pd.DataFrame(), " No comments fetched (comments may be disabled)"

        df = pd.DataFrame(rows)
        return df, f" Comments: {len(df)} fetched"

    except requests.exceptions.Timeout:
        return pd.DataFrame(), " Comments request timed out"
    except Exception as exc:
        return pd.DataFrame(), f" Comments error: {str(exc)[:80]}"



#  Search by keyword


def search_videos_by_title(
    keyword: str,
    api_key: str,
    max_results: int = 5,
) -> list[dict]:
    try:
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "q":          keyword,
                "key":        api_key,
                "part":       "snippet",
                "type":       "video",
                "maxResults": max_results,
            },
            timeout=15,
        )
        data = resp.json()
        results = []
        for item in data.get("items", []):
            vid_id = item.get("id", {}).get("videoId", "")
            sn = item.get("snippet", {})
            if not vid_id:
                continue
            results.append({
                "video_id":      vid_id,
                "title":         sn.get("title", ""),
                "channel_title": sn.get("channelTitle", ""),
                "published_at":  sn.get("publishedAt", "")[:10],
                "thumbnail_url": sn.get("thumbnails", {}).get("medium", {}).get("url", ""),
            })
        return results
    except Exception:
        return []