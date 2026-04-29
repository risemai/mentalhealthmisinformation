"""
charts.py — All Plotly chart builders. Pure functions, no Streamlit imports.
"""

from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

#  Shared theme ─
DARK_BG     = "#0d0f14"
CARD_BG     = "#13161e"
BORDER      = "#1e2330"
TEXT_MAIN   = "#e8eaf0"
TEXT_DIM    = "#5a6070"
CYAN        = "#00d4ff"
GREEN       = "#00e5a0"
RED         = "#ff4757"
AMBER       = "#ffb347"
PURPLE      = "#b388ff"
BLUE        = "#4a8eff"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'DM Mono', monospace", color=TEXT_MAIN, size=12),
    margin=dict(l=20, r=20, t=40, b=20),
)


#  Misinformation Gauge 

def misinfo_gauge(score: float, label: str) -> go.Figure:
    """Gauge chart for misinformation confidence score (0–1)."""
    pct = score * 100
    if score < 0.35:
        bar_color = GREEN
    elif score < 0.65:
        bar_color = AMBER
    else:
        bar_color = RED

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        number={"suffix": "%", "font": {"size": 32, "color": bar_color, "family": "'DM Mono', monospace"}},
        delta={"reference": 50, "increasing": {"color": RED}, "decreasing": {"color": GREEN}},
        title={"text": label, "font": {"size": 13, "color": TEXT_DIM}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": BORDER,
                "tickfont": {"color": TEXT_DIM, "size": 10},
            },
            "bar": {"color": bar_color, "thickness": 0.3},
            "bgcolor": CARD_BG,
            "borderwidth": 0,
            "steps": [
                {"range": [0, 35],  "color": "#0d1f18"},
                {"range": [35, 65], "color": "#1f1a0d"},
                {"range": [65, 100],"color": "#1f0d0d"},
            ],
            "threshold": {
                "line": {"color": TEXT_MAIN, "width": 2},
                "thickness": 0.75,
                "value": pct,
            },
        },
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=260)
    return fig


#  Sentiment Donut ─

def sentiment_donut(summary: Dict) -> go.Figure:
    """Donut chart: Positive / Negative / Neutral breakdown."""
    labels  = ["Positive Engagement", "Neutral", "Negative Engagement"]
    values  = [summary["POSITIVE"], summary["NEUTRAL"], summary["NEGATIVE"]]
    colors  = [GREEN, TEXT_DIM, RED]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color=DARK_BG, width=3)),
        textinfo="label+percent",
        textfont=dict(family="'DM Mono', monospace", size=11, color=TEXT_MAIN),
        hovertemplate="<b>%{label}</b><br>%{value} comments (%{percent})<extra></extra>",
        rotation=90,
    ))

    # Centre annotation
    avg = summary.get("avg_compound", 0)
    overall = "😊 Positive Engagement" if avg > 0.05 else ("😟 Negative Engagement" if avg < -0.05 else "😐 Mixed")
    fig.add_annotation(
        text=f"<b>{overall}</b><br><span style='font-size:11px;color:{TEXT_DIM}'>{summary['total']} comments</span>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=13, color=TEXT_MAIN, family="'DM Mono', monospace"),
        align="center",
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
                      legend=dict(orientation="h", y=-0.08, font=dict(size=11)))
    return fig


#  Keyword Bar Chart ─

def _hex_to_rgba(hex_color: str, alpha: float = 0.20) -> str:
    """Convert a 6-digit hex colour string to a valid rgba() string for Plotly."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def keyword_bar(
    keywords: List[Tuple[str, float]],
    title: str = "Top Keywords",
    color: str = CYAN,
) -> go.Figure:
    if not keywords:
        return _empty_fig(title)

    words, weights = zip(*keywords[:15])
    # Normalize to 0-100
    max_w = max(weights) or 1
    norm = [w / max_w * 100 for w in weights]

    fig = go.Figure(go.Bar(
        x=norm,
        y=words,
        orientation="h",
        marker=dict(
            color=norm,
            # Plotly colorscale requires valid colour strings — rgba() not 8-digit hex
            colorscale=[[0, _hex_to_rgba(color, 0.20)], [1, color]],
            line=dict(width=0),
        ),
        text=[f"{w:.0f}" for w in weights],
        textposition="inside",
        textfont=dict(size=10, color=DARK_BG),
        hovertemplate="<b>%{y}</b><br>Weight: %{text}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font=dict(size=13, color=TEXT_DIM), x=0),
        height=380,
        yaxis=dict(autorange="reversed", tickfont=dict(size=11), gridcolor=BORDER),
        xaxis=dict(showticklabels=False, gridcolor=BORDER),
        bargap=0.35,
    )
    return fig


#  Stream Trust Bars ─

def stream_trust_bars(stream_details: Dict) -> go.Figure:
    """Horizontal bar chart for per-stream misinfo scores."""
    labels = list(stream_details.keys())
    values = [round(v * 100, 1) for v in stream_details.values()]
    colors = [RED if v > 50 else (AMBER if v > 30 else GREEN) for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=[l.replace("_", " ").title() for l in labels],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v}%" for v in values],
        textposition="outside",
        textfont=dict(size=11, color=TEXT_MAIN),
        hovertemplate="<b>%{y}</b><br>Score: %{x}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Per-Stream Analysis", font=dict(size=13, color=TEXT_DIM), x=0),
        height=220,
        xaxis=dict(range=[0, 110], showticklabels=False, gridcolor=BORDER),
        yaxis=dict(tickfont=dict(size=11)),
        bargap=0.4,
    )
    return fig


#  Modality Misinformation Distribution ─

def modality_misinfo_distribution(modality_analysis: Dict) -> go.Figure:
    """
    Grouped bar chart — Misinformation Score vs Not-Misinformation Score per modality.

    Bars are derived directly from the model's per-stream softmax probabilities
    (values in ``modality_analysis[modality]["misinfo_pct"]`` /
    ``modality_analysis[modality]["credible_pct"]``).
    Each pair of bars sums to exactly 100 % because they are complementary
    softmax outputs from the same binary classification head.

    Parameters
    ----------
    modality_analysis : dict
        Mapping  {"text": {...}, "audio": {...}, "video": {...}}  as returned by
        ``analyzer._compute_modality_analysis()`` — one sub-dict per stream.
    """
    MODALITIES = ["Text", "Audio", "Video"]
    KEYS       = ["text", "audio", "video"]

    misinfo_pcts  = [modality_analysis.get(k, {}).get("misinfo_pct",  50.0) for k in KEYS]
    credible_pcts = [modality_analysis.get(k, {}).get("credible_pct", 50.0) for k in KEYS]
    logit_tips    = [
        (f"logit_m={modality_analysis.get(k, {}).get('misinfo_logit', 0.0):+.4f} | "
         f"logit_c={modality_analysis.get(k, {}).get('credible_logit', 0.0):+.4f}")
        for k in KEYS
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Misinformation Score",
        x=MODALITIES,
        y=misinfo_pcts,
        marker=dict(
            color=[RED, RED, RED],
            opacity=0.88,
            line=dict(color=DARK_BG, width=1),
        ),
        text=[f"{v:.1f}%" for v in misinfo_pcts],
        textposition="outside",
        textfont=dict(size=11, color=RED),
        customdata=logit_tips,
        hovertemplate=(
            "<b>%{x} — Misinformation</b><br>"
            "Softmax: %{y:.2f}%<br>"
            "%{customdata}<extra></extra>"
        ),
    ))

    fig.add_trace(go.Bar(
        name="Not Misinformation",
        x=MODALITIES,
        y=credible_pcts,
        marker=dict(
            color=[GREEN, GREEN, GREEN],
            opacity=0.88,
            line=dict(color=DARK_BG, width=1),
        ),
        text=[f"{v:.1f}%" for v in credible_pcts],
        textposition="outside",
        textfont=dict(size=11, color=GREEN),
        customdata=logit_tips,
        hovertemplate=(
            "<b>%{x} — Credible</b><br>"
            "Softmax: %{y:.2f}%<br>"
            "%{customdata}<extra></extra>"
        ),
    ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="Modality Misinformation Distribution",
            font=dict(size=13, color=TEXT_DIM),
            x=0,
        ),
        barmode="group",
        height=280,
        xaxis=dict(
            title="Modality",
            tickfont=dict(size=12),
            gridcolor=BORDER,
        ),
        yaxis=dict(
            title="Softmax Score (%)",
            range=[0, 115],
            gridcolor=BORDER,
            ticksuffix="%",
        ),
        legend=dict(
            orientation="h",
            y=1.12,
            font=dict(size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        bargap=0.22,
        bargroupgap=0.06,
    )
    return fig


#  Trust Score by Modality ─

def trust_score_by_modality(modality_analysis: Dict) -> go.Figure:
    """
    Vertical bar chart — model's reliability/trustworthiness coefficient per stream.

    Trust is computed as a linear combination of model confidence (1 – Shannon entropy)
    and content-richness, both derived from the actual inference pass, never fixed.

    Parameters
    ----------
    modality_analysis : dict
        Same structure as ``modality_misinfo_distribution``.
    """
    MODALITIES = ["Text", "Audio", "Video"]
    KEYS       = ["text", "audio", "video"]

    trust_vals = [modality_analysis.get(k, {}).get("trust_score", 0.0) for k in KEYS]
    bar_colors = [
        (GREEN if v >= 60 else (AMBER if v >= 35 else RED))
        for v in trust_vals
    ]

    fig = go.Figure(go.Bar(
        x=MODALITIES,
        y=trust_vals,
        marker=dict(
            color=bar_colors,
            opacity=0.88,
            line=dict(color=DARK_BG, width=1),
        ),
        text=[f"{v:.1f}%" for v in trust_vals],
        textposition="outside",
        textfont=dict(size=11, color=TEXT_MAIN),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Trust Level: %{y:.2f}%<br>"
            "<i>Derived from (1 – H_entropy) × content_richness</i>"
            "<extra></extra>"
        ),
    ))

    # Reference lines
    for level, label, color in [(80, "High Trust", GREEN), (50, "Threshold", AMBER)]:
        fig.add_hline(
            y=level,
            line=dict(color=color, width=1, dash="dot"),
            annotation_text=label,
            annotation_position="right",
            annotation_font=dict(size=9, color=color),
        )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="Trust Score by Modality",
            font=dict(size=13, color=TEXT_DIM),
            x=0,
        ),
        height=280,
        xaxis=dict(
            title="Modality",
            tickfont=dict(size=12),
            gridcolor=BORDER,
        ),
        yaxis=dict(
            title="Trust Level (%)",
            range=[0, 115],
            gridcolor=BORDER,
            ticksuffix="%",
        ),
        bargap=0.38,
    )
    return fig


#  Uncertainty Analysis 

def uncertainty_analysis(modality_analysis: Dict) -> go.Figure:
    """
    Vertical bar chart — Shannon entropy of the model's softmax distribution per stream.

    High entropy ( → 100 %) means the model is maximally unsure (uniform distribution).
    Low entropy ( → 0 %) means the model is highly confident in its prediction.
    Values come directly from H = –Σ p·log₂(p) over the two softmax outputs.

    Parameters
    ----------
    modality_analysis : dict
        Same structure as ``modality_misinfo_distribution``.
    """
    MODALITIES = ["Text", "Audio", "Video"]
    KEYS       = ["text", "audio", "video"]

    uncertainty_vals = [modality_analysis.get(k, {}).get("uncertainty", 100.0) for k in KEYS]
    misinfo_pcts     = [modality_analysis.get(k, {}).get("misinfo_pct", 50.0)  for k in KEYS]

    # Colour encodes confidence direction: red = uncertain, green = confident
    bar_colors = [
        (GREEN if v <= 35 else (AMBER if v <= 65 else RED))
        for v in uncertainty_vals
    ]

    fig = go.Figure(go.Bar(
        x=MODALITIES,
        y=uncertainty_vals,
        marker=dict(
            color=bar_colors,
            opacity=0.88,
            line=dict(color=DARK_BG, width=1),
        ),
        text=[f"{v:.1f}%" for v in uncertainty_vals],
        textposition="outside",
        textfont=dict(size=11, color=TEXT_MAIN),
        customdata=[[f"p_misinfo={m:.1f}%"] for m in misinfo_pcts],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Uncertainty (H): %{y:.2f}%<br>"
            "%{customdata[0]}<br>"
            "<i>H = –Σ p·log₂(p), normalised to %</i>"
            "<extra></extra>"
        ),
    ))

    # Max-entropy reference
    fig.add_hline(
        y=100,
        line=dict(color=RED, width=1, dash="dot"),
        annotation_text="Max Entropy (no signal)",
        annotation_position="right",
        annotation_font=dict(size=9, color=RED),
    )
    fig.add_hline(
        y=50,
        line=dict(color=AMBER, width=1, dash="dot"),
        annotation_text="Mid Uncertainty",
        annotation_position="right",
        annotation_font=dict(size=9, color=AMBER),
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="Uncertainty Analysis (Shannon Entropy)",
            font=dict(size=13, color=TEXT_DIM),
            x=0,
        ),
        height=280,
        xaxis=dict(
            title="Modality",
            tickfont=dict(size=12),
            gridcolor=BORDER,
        ),
        yaxis=dict(
            title="Uncertainty (%)",
            range=[0, 120],
            gridcolor=BORDER,
            ticksuffix="%",
        ),
        bargap=0.38,
    )
    return fig


#  Comment Sentiment Timeline 

def sentiment_timeline(comments_df: pd.DataFrame, sentiments: List[Dict]) -> go.Figure:
    """Scatter: comment likes vs. sentiment compound score."""
    if comments_df.empty:
        return _empty_fig("Comment Sentiment Distribution")

    df = comments_df.copy()
    df["compound"] = [s.get("compound", 0) for s in sentiments]
    df["label"]    = [s.get("label", "NEUTRAL") for s in sentiments]
    df["color"]    = df["label"].map({"POSITIVE": GREEN, "NEGATIVE": RED, "NEUTRAL": AMBER})
    df["text_short"] = df["text"].str[:80] + "…"

    DISPLAY_NAME = {"POSITIVE": "Positive Engagement", "NEGATIVE": "Negative Engagement", "NEUTRAL": "Neutral"}
    fig = go.Figure()
    for lbl, clr in [("POSITIVE", GREEN), ("NEGATIVE", RED), ("NEUTRAL", AMBER)]:
        sub = df[df["label"] == lbl]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub.index,
            y=sub["compound"],
            mode="markers",
            name=DISPLAY_NAME.get(lbl, lbl),
            marker=dict(
                size=np.clip(np.log1p(sub["likes"].fillna(0)) * 4 + 4, 4, 20),
                color=clr,
                opacity=0.75,
                line=dict(width=0),
            ),
            text=sub["text_short"],
            hovertemplate="<b>%{text}</b><br>Sentiment: %{y:.2f}<br>Likes: %{marker.size}<extra></extra>",
        ))

    fig.add_hline(y=0, line=dict(color=BORDER, width=1, dash="dot"))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Comment Sentiment (size = likes)", font=dict(size=13, color=TEXT_DIM), x=0),
        height=320,
        xaxis=dict(title="Comment index", gridcolor=BORDER, showgrid=False),
        yaxis=dict(title="Compound score", gridcolor=BORDER, range=[-1.1, 1.1]),
        legend=dict(orientation="h", y=1.12, font=dict(size=11)),
    )
    return fig


#  Positive vs Negative Keyword Comparison ─

def keyword_comparison(
    pos_kw: List[Tuple[str, float]],
    neg_kw: List[Tuple[str, float]],
) -> go.Figure:
    """Diverging bar chart: positive keywords right, negative left."""
    if not pos_kw and not neg_kw:
        return _empty_fig("Sentiment Keywords")

    top = 10
    pos_kw = pos_kw[:top]
    neg_kw = neg_kw[:top]

    fig = go.Figure()

    if pos_kw:
        pw, pv = zip(*pos_kw)
        max_p = max(pv) or 1
        fig.add_trace(go.Bar(
            name="Positive Engagement",
            y=list(pw),
            x=[v/max_p*100 for v in pv],
            orientation="h",
            marker_color=GREEN,
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>",
        ))

    if neg_kw:
        nw, nv = zip(*neg_kw)
        max_n = max(nv) or 1
        fig.add_trace(go.Bar(
            name="Negative Engagement",
            y=list(nw),
            x=[-v/max_n*100 for v in nv],
            orientation="h",
            marker_color=RED,
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>",
        ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Sentiment-Weighted Keywords", font=dict(size=13, color=TEXT_DIM), x=0),
        height=360,
        barmode="overlay",
        xaxis=dict(title="← Negative  |  Positive →", gridcolor=BORDER, zeroline=True,
                   zerolinecolor=BORDER, zerolinewidth=2),
        yaxis=dict(tickfont=dict(size=10)),
        legend=dict(orientation="h", y=1.1),
    )
    return fig


#  Helpers ─

def _empty_fig(title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False,
                       font=dict(size=14, color=TEXT_DIM))
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(text=title, x=0), height=250)
    return fig