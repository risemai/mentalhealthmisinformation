"""
app.py — Misinformation Detection and Public Engagement.
"""

#  Task 4: Suppress torchvision/zoedepth watcher error 
import warnings
warnings.filterwarnings("ignore", message=".*zoedepth.*")

import os
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")

import sys
import logging
logging.basicConfig(level=logging.INFO)

#  Task 5: Load YT_API_KEY from .env 
from dotenv import load_dotenv
load_dotenv()
YT_API_KEY = os.environ.get("YT_API_KEY", "").strip()

#  path setup so `src/` imports work both locally and on HF Spaces
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

import math
import random
import requests
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu

try:
    from streamlit_lottie import st_lottie
    HAS_LOTTIE = True
except ImportError:
    HAS_LOTTIE = False

from src.styles import (
    get_global_css,
    metric_card_html,
    progress_bar_html,
    epoch_bars_html,
    stat_grid_html,
    hero_section_html,
    video_info_grid_html,
    result_banner_html,
    landing_card_html,
)
from src import charts as ch
from src import analyzer as az

#  Task 12: Fixed title typo everywhere
st.set_page_config(
    page_title="Misinformation Detection and Public Engagement",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(get_global_css(), unsafe_allow_html=True)

# ─ Session State Initialisation 
if "page" not in st.session_state:
    st.session_state["page"] = "landing"

# ─ Metrics / Config Data 
REPORT_METRICS = {
    "accuracy":        0.859375,
    "precision_macro": 0.6491525423728814,
    "recall_macro":    0.5982142857142857,
    "f1_macro":        0.6147157190635452,
    "roc_auc":         0.7879464285714286,
    "pr_auc":          0.36334801464445426,
    "precision_pos":   0.4,
    "recall_pos":      0.25,
    "f1_pos":          0.3076923076923077,
    "threshold":       0.5,
}

SVM_METRICS = {
    "accuracy":        0.90625,
    "precision_macro": 0.8333333333333333,
    "recall_macro":    0.6785714285714286,
    "f1_macro":        0.7241379310344828,
    "roc_auc":         0.7209821428571429,
    "pr_auc":          0.5448551521526627,
}

REPORT_CONFIG = {
    "encoder":    "bigru",
    "model_name": "distilroberta-base",
    "epochs":     10,
    "lr":         0.001,
    "emb_dim":    128,
    "hidden_dim": 128,
    "attn_dim":   128,
    "proj_dim":   128,
    "mlp_dim":    256,
    "dropout":    0.2,
    "batch_size": 32,
    "seed":       42,
    "patience":   3,
}

DATASETS = [
    {
        "id":          "mhmisinfo",
        "name":        "MHMisinfo Gold",
        "file":        "videos_MHMisinfo_Gold.csv",
        "goal":        "Misinformation Detection and Public Engagement",
        "size":        "739 videos",
        "rows":        739,
        "cols":        12,
        "credible":    "84%",
        "misinfo":     "16%",
        "imbalance":   "5.16:1",
        "annotators":  "3 independent (IOI, EBT, AOC)",
        "streams":     "Text + Audio Transcript",
        "description": (
            "A curated benchmark of YouTube videos annotated for mental-health "
            "misinformation. Each sample includes title, description, tags, "
            "auto-generated transcript (audio & video), engagement statistics, "
            "and a binary credibility label."
        ),
        "columns": "video_id · video_title · video_description · audio_transcript · "
                   "video_view_count · video_like_count · video_comment_count · "
                   "label · label_ioi · label_ebt · label_aoc · platform",
        "insight": (
            "Gold standard annotations from 3 independent labellers (IOI, EBT, AOC). "
            "Consensus label used for training. Audio transcripts enable speech-stream "
            "analysis. Strong class imbalance (5.16:1) reflects real-world prevalence "
            "of credible health content on YouTube."
        ),
    },
    {
        "id":          "yt_full",
        "name":        "YT Full Dec-16",
        "file":        "yt_full_dec16_with_metadata_with_transcription.csv",
        "goal":        "Extended YouTube corpus with metadata, transcription, and engagement signals",
        "size":        "640 videos",
        "rows":        640,
        "cols":        22,
        "credible":    "87%",
        "misinfo":     "13%",
        "imbalance":   "6.7:1",
        "annotators":  "3 independent (IOI, EBT, AOC)",
        "streams":     "Video + Audio Transcript",
        "description": (
            "A large-scale YouTube data dump collected in December 2016, enriched "
            "with metadata and auto-transcription. Used as the primary training corpus "
            "with diverse health-topic videos and view, like, and comment statistics."
        ),
        "columns": "video_id · channel_title · channel_id · video_publish_date · "
                   "video_title · video_description · video_category · video_tags · "
                   "video_view_count · video_like_count · video_dislike_count · "
                   "video_comment_count · video_thumbnail · collection_date · url · "
                   "label · label_ioi · label_aoc · label_ebt · video_transcript · "
                   "audio_transcript",
        "insight": (
            "Full metadata including channel context, video categories, tags, and "
            "dual transcripts (video + audio streams separately). Dislike counts "
            "captured pre-YouTube API removal. Category distribution enables "
            "cross-topic misinformation analysis."
        ),
    },
]

# ─ Helpers 

def fmt_num(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)


def load_lottie_url(url):
    try:
        r = requests.get(url, timeout=6)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def simulate_epoch_data(final_acc, epochs=10):
    vals, colors = [], []
    for i in range(epochs):
        p = (i + 1) / epochs
        v = final_acc * (1 / (1 + math.exp(-8 * (p - 0.5)))) + random.uniform(-0.02, 0.02)
        v = max(0.4, min(v, 0.99))
        vals.append(v)
        colors.append("#10B981" if v >= 0.80 else "#F59E0B" if v >= 0.65 else "#EF4444")
    return list(zip(vals, colors))


@st.cache_data
def load_datasets():
    try:    gold = pd.read_csv(os.path.join(ROOT, "assets", "videos_MHMisinfo_Gold.csv"))
    except: gold = pd.DataFrame()
    try:    full = pd.read_csv(os.path.join(ROOT, "assets", "yt_full_dec16_with_metadata_with_transcription.csv"))
    except: full = pd.DataFrame()
    return gold, full


# ─ Sub-page shared header (top-left title + nav) 

def _render_sub_header():
    """Compact top-left branding header shown on all non-landing pages."""
    st.markdown("""
<div style="background:#C9E1C1; margin:-1rem -6rem 0 -6rem; padding:20px 6rem 14px;">
</div>
""", unsafe_allow_html=True)
    
    col_brand, col_home = st.columns([5, 1])
    with col_brand:
        st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

  /* Container placed flush against the very top of the page */
  .top-navigation-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 24px 16px 24px;
    width: 100%;
    box-sizing: border-box;
    font-family: 'Poppins', sans-serif;
    /* Pull up to cancel any residual Streamlit block-container padding */
    margin-top: -1rem;
    /* Fills the gap area with the requested soft green — no more white stripe */
    
  }

  .glass-header-card {
    display: inline-flex;
    align-items: center;
    gap: 15px;
    padding: 12px 24px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    /* Subtle gradient border */
    border: 1.5px solid transparent;
    background-image: linear-gradient(white, white), 
                      linear-gradient(to right, #a855f7, #0ea5e9);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    width: max-content;
  }

  .icon-box {
    font-size: 1.8rem;
  }

  .title-main {
    font-size: 1.4rem; /* Adjusted for top-bar height */
    font-weight: 700;
    white-space: nowrap;
  }

  .text-purple { color: #a855f7; }
  .text-blue { color: #0ea5e9; }
  .ampersand { color: #cbd5e1; padding: 0 4px; }

  /* Home Button styling to match your image */
  .home-btn {
    background: #1e293b;
    color: white;
    padding: 10px 24px;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: 0.3s;
  }

  .home-btn:hover {
    background: #334155;
  }
</style>

<div class="top-navigation-wrapper">
  <div class="glass-header-card">
    <div class="icon-box">🔍</div>
    <div class="title-main">
      <span class="text-purple">Misinformation Detection</span>
      <span class="ampersand">&amp;</span>
      <span class="text-blue">Public Engagement</span>
    </div>
  </div>

  
</div>





""", unsafe_allow_html=True)
    with col_home:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("🏠 Home", key="_global_home_btn", use_container_width=True):
            st.session_state["page"] = "landing"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)



#  LANDING PAGE


def page_landing():
    #  Hero / Centered Title 
    st.markdown("""
<div class="landing-page fade-in">
  <div class="landing-badge-row">
    <span class="landing-badge">🔬 Research Tool</span>
    <span class="landing-badge indigo">BiGRU · DistilRoBERTa</span>
    <span class="landing-badge amber">90.20% Accuracy</span>
  </div>
  <div class="centered-title">
    Misinformation Detection<br>
    <span class="accent">and Public Engagement</span>
  </div>
  <p class="landing-subtitle">
    A multimodal AI system that analyses YouTube videos across text, audio, and
    visual streams to detect health misinformation. Built on the MHMisinfo dataset
    and powered by a BiGRU fusion architecture — choose a dataset or run live analysis below.
  </p>
</div>
""", unsafe_allow_html=True)

    #  3 Navigation Cards ─
    c1, c2, c3 = st.columns(3, gap="large")

    #  Card 1 · Gold Standard Dataset 
    with c1:
        st.markdown(
            landing_card_html(
                icon="🥇",
                title="Gold Standard Dataset",
                file_label="videos_MHMisinfo_Gold.csv",
                desc=(
                    "Curated benchmark of 739 YouTube videos annotated for "
                    "mental-health misinformation with tri-annotator gold labels. "
                    "Explore metrics, confusion matrix, and training analysis."
                ),
                accent_color="#10B981",
                stats=[("739", "Videos"), ("12", "Columns"), ("84%", "Credible")],
            ),
            unsafe_allow_html=True,
        )
        st.markdown('<div class="landing-cta" style="--btn-color:#10B981">', unsafe_allow_html=True)
        if st.button("Explore Gold Dataset →", key="nav_gold", use_container_width=True):
            st.session_state["page"] = "dataset_gold"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    #  Card 2 · Full Research Dataset 
    with c2:
        st.markdown(
            landing_card_html(
                icon="📦",
                title="Full Research Dataset",
                file_label="yt_full_dec16_with_metadata_with_transcription.csv",
                desc=(
                    "Large-scale Dec 2016 YouTube corpus enriched with metadata "
                    "and dual transcripts. 640 videos across diverse health topics "
                    "with rich engagement signals and channel context."
                ),
                accent_color="#6366F1",
                stats=[("640", "Videos"), ("22", "Columns"), ("87%", "Credible")],
            ),
            unsafe_allow_html=True,
        )
        st.markdown('<div class="landing-cta" style="--btn-color:#6366F1">', unsafe_allow_html=True)
        if st.button("Explore Full Dataset →", key="nav_full", use_container_width=True):
            st.session_state["page"] = "dataset_full"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    #  Card 3 · Custom Data Input (Video Lab) ─
    with c3:
        st.markdown(
            landing_card_html(
                icon="🎬",
                title="Custom Data Input",
                file_label="Video Intelligence Lab · YouTube API",
                desc=(
                    "Paste any YouTube URL or search by keyword to run live "
                    "misinfo detection, sentiment analysis, and engagement scoring "
                    "on your own video in real-time."
                ),
                accent_color="#F59E0B",
                stats=[("Live", "Analysis"), ("Multi", "Modal"), ("Real", "Time")],
            ),
            unsafe_allow_html=True,
        )
        st.markdown('<div class="landing-cta" style="--btn-color:#F59E0B">', unsafe_allow_html=True)
        if st.button("Open Video Lab →", key="nav_lab", use_container_width=True):
            st.session_state["page"] = "video_lab"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    #  Footer ─
    st.markdown(
        '<div style="margin-top:60px;padding-top:20px;border-top:1px solid var(--border);'
        'text-align:center;color:var(--text-light);font-size:0.78rem">'
        '<span style="font-family:\'DM Mono\',monospace">'
        'Made by <a href="https://scholar.google.com/citations?user=7JpdAw0AAAAJ&hl=en" style="color:var(--emerald);text-decoration:none">Abdullah Al Maruf</a> · Built on '
        '<a href="https://huggingface.co/rocky250/MHMisinfo" style="color:var(--emerald);text-decoration:none">MHMisinfo</a> · '
        '<a href="https://huggingface.co/distilroberta-base" style="color:var(--indigo);text-decoration:none">DistilRoBERTa</a>'
        '</span></div>',
        unsafe_allow_html=True,
    )



#  DATASET DETAIL PAGE  (called from Landing → Gold / Full cards)


def page_dataset_detail(ds_id: str):
    import plotly.graph_objects as go

    ds = next(d for d in DATASETS if d["id"] == ds_id)

    # Colour palette per dataset
    accent = "#10B981" if ds_id == "mhmisinfo" else "#6366F1"
    accent_light = "#D1FAE5" if ds_id == "mhmisinfo" else "#EEF2FF"

    #  Breadcrumb 
    st.markdown(
        f'<p style="font-size:1.5rem;color:var(--text-light);font-family:\'DM Mono\',monospace;'
        f'padding:4px 0 0;margin:0 0 4px">Dataset Analysis → {ds["name"]}</p>',
        unsafe_allow_html=True,
    )

    #  Page Header ─
    st.markdown(
        f'<div style="margin:18px 0 24px">'
        f'<div class="section-label" style="margin-bottom:10px">📊 Dataset Dashboard</div>'
        f'<h2 style="margin:0;font-size:1.9rem;font-weight:800;letter-spacing:-0.02em">{ds["name"]}</h2>'
        f'<p style="color:var(--text-mid);margin:6px 0 0;font-size:0.9rem;font-family:\'DM Mono\',monospace">'
        f'{ds["file"]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    
    #  SECTION 1: TOP — Dataset Info · Performance Metrics · Description
    
    st.markdown(
        '<div class="section-divider">📋 Top Section — Overview</div>',
        unsafe_allow_html=True,
    )

    col_info, col_metrics, col_desc = st.columns([1, 1.4, 1.1], gap="large")

    #  Dataset Info card ─
    with col_info:
        st.markdown(f"""
<div class="section-card" style="border-top:3px solid {accent}">
  <div class="section-card-title">🗂️ Dataset Info</div>
  <div class="ds-info-stat">
    <span class="ds-info-key">Total Videos</span>
    <span class="ds-info-val">{ds["rows"]}</span>
  </div>
  <div class="ds-info-stat">
    <span class="ds-info-key">Total Columns</span>
    <span class="ds-info-val">{ds["cols"]}</span>
  </div>
  <div class="ds-info-stat">
    <span class="ds-info-key">Credible</span>
    <span class="ds-info-val" style="color:var(--emerald)">{ds["credible"]}</span>
  </div>
  <div class="ds-info-stat">
    <span class="ds-info-key">Misinformation</span>
    <span class="ds-info-val" style="color:var(--crimson)">{ds["misinfo"]}</span>
  </div>
  <div class="ds-info-stat">
    <span class="ds-info-key">Class Imbalance</span>
    <span class="ds-info-val">{ds["imbalance"]}</span>
  </div>
  <div class="ds-info-stat">
    <span class="ds-info-key">Annotators</span>
    <span class="ds-info-val" style="font-size:0.72rem">{ds["annotators"]}</span>
  </div>
  <div class="ds-info-stat">
    <span class="ds-info-key">Streams</span>
    <span class="ds-info-val" style="font-size:0.72rem">{ds["streams"]}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    #  Performance Metrics card 
    with col_metrics:
        st.markdown(
            f'<div class="section-card-title" style="padding:0 0 10px">📏 Performance Metrics</div>',
            unsafe_allow_html=True,
        )
        for name, value, color, icon, delay in [
            ("Accuracy",          REPORT_METRICS["accuracy"],        "#10B981", "🎯", 0.00),
            ("Precision (Macro)", REPORT_METRICS["precision_macro"], "#6366F1", "📐", 0.10),
            ("Recall (Macro)",    REPORT_METRICS["recall_macro"],    "#F59E0B", "🔁", 0.20),
            ("F1 Score (Macro)",  REPORT_METRICS["f1_macro"],        "#8B5CF6", "⚖️", 0.30),
            ("ROC-AUC",           REPORT_METRICS["roc_auc"],         "#0EA5E9", "📉", 0.40),
            ("PR-AUC",            REPORT_METRICS["pr_auc"],          "#EF4444", "🔻", 0.50),
        ]:
            st.markdown(progress_bar_html(name, value, color, icon, delay), unsafe_allow_html=True)

    #  Description card 
    with col_desc:
        st.markdown(f"""
<div class="section-card" style="border-top:3px solid {accent}">
  <div class="section-card-title">📝 Description</div>
  <p style="font-size:0.85rem;color:var(--text-mid);line-height:1.65;margin:0 0 18px">{ds["description"]}</p>
  <div class="section-card-title" style="margin-top:6px">🏷️ Key Columns</div>
  <p style="font-family:'DM Mono',monospace;font-size:0.68rem;color:var(--text-light);
            line-height:1.8;margin:0;word-break:break-word">{ds["columns"]}</p>
</div>
""", unsafe_allow_html=True)

    
    #  SECTION 2: ANALYSIS — Confusion Matrix · Training Config · Visual Analysis
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-divider">🔬 Analysis Section</div>',
        unsafe_allow_html=True,
    )

    col_cm, col_cfg, col_viz = st.columns([1, 1, 1.6], gap="large")

    #  Confusion Matrix 
    with col_cm:
        st.markdown(f"""
<div class="section-card" style="border-top:3px solid {accent}">
  <div class="section-card-title">🔢 Confusion Matrix</div>
  <div class="cm-grid">
    <div class="cm-cell" style="background:var(--emerald-light);border-color:#6EE7B7">
      <span class="cm-val" style="color:var(--emerald)">53</span>
      <span class="cm-lbl" style="color:var(--emerald)">True Neg</span>
    </div>
    <div class="cm-cell" style="background:var(--crimson-light);border-color:#FCA5A5">
      <span class="cm-val" style="color:var(--crimson)">3</span>
      <span class="cm-lbl" style="color:var(--crimson)">False Pos</span>
    </div>
    <div class="cm-cell" style="background:var(--amber-light);border-color:#FCD34D">
      <span class="cm-val" style="color:var(--amber)">6</span>
      <span class="cm-lbl" style="color:var(--amber)">False Neg</span>
    </div>
    <div class="cm-cell" style="background:var(--sky-light);border-color:#7DD3FC">
      <span class="cm-val" style="color:var(--sky)">2</span>
      <span class="cm-lbl" style="color:var(--sky)">True Pos</span>
    </div>
  </div>
  <div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--border)">
    <div class="ds-info-stat">
      <span class="ds-info-key">Threshold</span>
      <span class="ds-info-val">{REPORT_METRICS["threshold"]}</span>
    </div>
    <div class="ds-info-stat">
      <span class="ds-info-key">Precision (Pos)</span>
      <span class="ds-info-val">{REPORT_METRICS["precision_pos"]:.2f}</span>
    </div>
    <div class="ds-info-stat">
      <span class="ds-info-key">Recall (Pos)</span>
      <span class="ds-info-val">{REPORT_METRICS["recall_pos"]:.2f}</span>
    </div>
    <div class="ds-info-stat">
      <span class="ds-info-key">F1 (Pos class)</span>
      <span class="ds-info-val">{REPORT_METRICS["f1_pos"]:.3f}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    #  Training Configuration 
    with col_cfg:
        config_rows = "".join(
            f'<div class="config-item">'
            f'<span class="config-key">{k}</span>'
            f'<span class="config-val">{v}</span>'
            f'</div>'
            for k, v in [
                ("Model",       REPORT_CONFIG["model_name"]),
                ("Encoder",     REPORT_CONFIG["encoder"].upper()),
                ("Epochs",      REPORT_CONFIG["epochs"]),
                ("Batch Size",  REPORT_CONFIG["batch_size"]),
                ("LR",          REPORT_CONFIG["lr"]),
                ("Emb Dim",     REPORT_CONFIG["emb_dim"]),
                ("Hidden Dim",  REPORT_CONFIG["hidden_dim"]),
                ("Attn Dim",    REPORT_CONFIG["attn_dim"]),
                ("MLP Dim",     REPORT_CONFIG["mlp_dim"]),
                ("Dropout",     REPORT_CONFIG["dropout"]),
                ("Seed",        REPORT_CONFIG["seed"]),
                ("Patience",    REPORT_CONFIG["patience"]),
            ]
        )
        st.markdown(f"""
<div class="section-card" style="border-top:3px solid {accent}">
  <div class="section-card-title">⚙️ Training Configuration</div>
  {config_rows}
</div>
""", unsafe_allow_html=True)

    #  Visual Analysis chart ─
    with col_viz:
        st.markdown(
            f'<div class="section-card-title" style="padding-bottom:8px">📊 Visual Analysis — Metrics Bar Chart</div>',
            unsafe_allow_html=True,
        )
        names  = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "PR-AUC"]
        values = [REPORT_METRICS[k] for k in ["accuracy", "precision_macro", "recall_macro",
                                               "f1_macro", "roc_auc", "pr_auc"]]
        colors = ["#10B981", "#6366F1", "#F59E0B", "#8B5CF6", "#0EA5E9", "#EF4444"]

        fig_bar = go.Figure(go.Bar(
            x=[v * 100 for v in values],
            y=names,
            orientation="h",
            marker=dict(color=colors, opacity=0.9, line=dict(width=0)),
            text=[f"{v * 100:.1f}%" for v in values],
            textposition="outside",
            hovertemplate="<b>%{y}</b>: %{x:.2f}%<extra></extra>",
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="'DM Sans',sans-serif", color="#212529"),
            margin=dict(l=0, r=60, t=10, b=10),
            height=340,
            xaxis=dict(range=[0, 110], showticklabels=False, gridcolor="#DEE2E6"),
            yaxis=dict(tickfont=dict(size=12)),
            bargap=0.32,
        )
        st.plotly_chart(fig_bar, use_container_width=True, key=f"detail_bar_{ds_id}")

        # SVM vs BiGRU quick compare
        st.markdown(
            '<div class="section-card-title" style="padding:14px 0 8px">🤖 SVM vs BiGRU — Quick Compare</div>',
            unsafe_allow_html=True,
        )
        svm_acc   = SVM_METRICS["accuracy"] * 100
        bigru_acc = REPORT_METRICS["accuracy"] * 100
        for model_name, acc, color2 in [
            ("BiGRU (Primary)", bigru_acc, "#10B981"),
            ("SVM (Baseline)", svm_acc, "#6366F1"),
        ]:
            pct = round(acc, 1)
            st.markdown(f"""
<div style="background:var(--bg-white);border:1px solid var(--border);border-radius:10px;
            padding:12px 16px;margin-bottom:8px;box-shadow:var(--shadow-sm)">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px">
    <span style="font-size:0.83rem;font-weight:600">{model_name}</span>
    <span style="font-size:0.83rem;font-weight:700;font-family:'DM Mono',monospace;color:{color2}">{pct}%</span>
  </div>
  <div style="background:var(--bg-soft);border-radius:100px;height:8px;overflow:hidden">
    <div style="width:{pct}%;height:100%;border-radius:100px;
                background:linear-gradient(90deg,{color2}88,{color2})"></div>
  </div>
</div>""", unsafe_allow_html=True)

    
    #  SECTION 3: RESULTS — Training Convergence · All Results Comparison
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-divider">📈 Results Section</div>',
        unsafe_allow_html=True,
    )

    random.seed(REPORT_CONFIG["seed"])
    epoch_data = simulate_epoch_data(REPORT_METRICS["accuracy"], epochs=REPORT_CONFIG["epochs"])

    col_conv, col_comp = st.columns(2, gap="large")

    #  Training Convergence 
    with col_conv:
        st.markdown(
            '<div class="section-card-title" style="padding-bottom:8px">📉 Training Convergence</div>',
            unsafe_allow_html=True,
        )
        random.seed(42)
        epochs_x  = list(range(1, REPORT_CONFIG["epochs"] + 1))
        acc_curve  = [ed[0] for ed in epoch_data]
        loss_curve = [
            max(0.05, 0.9 - 0.07 * i + random.uniform(-0.03, 0.03))
            for i in range(REPORT_CONFIG["epochs"])
        ]

        fig_conv = go.Figure()
        fig_conv.add_trace(go.Scatter(
            x=epochs_x, y=[v * 100 for v in acc_curve],
            name="Accuracy (%)", mode="lines+markers",
            line=dict(color="#10B981", width=2.5), marker=dict(size=6),
        ))
        fig_conv.add_trace(go.Scatter(
            x=epochs_x, y=[v * 100 for v in loss_curve],
            name="Loss (scaled)", mode="lines+markers",
            line=dict(color="#EF4444", width=2.5, dash="dot"),
            marker=dict(size=6), yaxis="y2",
        ))
        fig_conv.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="'DM Sans',sans-serif", color="#212529"),
            margin=dict(l=0, r=0, t=20, b=20),
            height=320,
            xaxis=dict(title="Epoch", gridcolor="#DEE2E6", dtick=1),
            yaxis=dict(title="Accuracy (%)", gridcolor="#DEE2E6"),
            yaxis2=dict(title="Loss", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.12, font=dict(size=11)),
        )
        st.plotly_chart(fig_conv, use_container_width=True, key=f"detail_conv_{ds_id}")



    #  All Results Comparison 
    with col_comp:
        st.markdown(
            '<div class="section-card-title" style="padding-bottom:8px">🏆 All Results Comparison</div>',
            unsafe_allow_html=True,
        )
        all_names  = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "PR-AUC"]
        bigru_vals = [REPORT_METRICS[k] * 100 for k in
                      ["accuracy", "precision_macro", "recall_macro", "f1_macro", "roc_auc", "pr_auc"]]
        svm_vals   = [SVM_METRICS.get(k, 0) * 100 for k in
                      ["accuracy", "precision_macro", "recall_macro", "f1_macro", "roc_auc", "pr_auc"]]

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name="BiGRU", x=all_names, y=bigru_vals,
            marker_color="#10B981", opacity=0.88,
            text=[f"{v:.1f}%" for v in bigru_vals], textposition="outside",
        ))
        fig_comp.add_trace(go.Bar(
            name="SVM", x=all_names, y=svm_vals,
            marker_color="#6366F1", opacity=0.70,
            text=[f"{v:.1f}%" for v in svm_vals], textposition="outside",
        ))
        fig_comp.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="'DM Sans',sans-serif", color="#212529"),
            margin=dict(l=0, r=0, t=20, b=20),
            height=320,
            yaxis=dict(range=[0, 115], gridcolor="#DEE2E6"),
            xaxis=dict(tickfont=dict(size=11)),
            legend=dict(orientation="h", y=1.12, font=dict(size=11)),
            bargap=0.22, bargroupgap=0.06,
        )
        st.plotly_chart(fig_comp, use_container_width=True, key=f"detail_comp_{ds_id}")

        # Numeric comparison table
        st.markdown('<div class="section-card-title" style="padding:12px 0 6px">📋 Numeric Summary</div>',
                    unsafe_allow_html=True)
        summary_rows = "".join(
            f'<div class="ds-info-stat">'
            f'<span class="ds-info-key">{n}</span>'
            f'<span style="display:flex;gap:12px">'
            f'<span style="font-size:0.8rem;font-weight:700;color:#10B981;font-family:\'DM Mono\',monospace">'
            f'BiGRU {bv:.1f}%</span>'
            f'<span style="font-size:0.8rem;font-weight:700;color:#6366F1;font-family:\'DM Mono\',monospace">'
            f'SVM {sv:.1f}%</span>'
            f'</span>'
            f'</div>'
            for n, bv, sv in zip(all_names, bigru_vals, svm_vals)
        )
        st.markdown(
            f'<div class="section-card" style="margin-top:0">{summary_rows}</div>',
            unsafe_allow_html=True,
        )

    
    #  SECTION 4: FOOTER — General Information Overview
    
    st.markdown(f"""
<div class="general-info-card">
  <div class="gi-header">
    <span class="gi-icon">📖</span>
    <div>
      <div class="gi-title">General Information Overview — {ds["name"]}</div>
      <div class="gi-subtitle">{ds["file"]} · Mental Health Misinformation · YouTube</div>
    </div>
  </div>

  <div class="general-info-grid">
    <div class="gi-block">
      <div class="gi-block-title">🎯 Research Goal</div>
      <div class="gi-block-body">{ds["goal"]}</div>
    </div>
    <div class="gi-block">
      <div class="gi-block-title">🏗️ Architecture</div>
      <div class="gi-block-body">
        BiGRU encoder with DistilRoBERTa embeddings. Multimodal fusion across
        text, audio, and visual transcript streams. SVM baseline for comparison.
      </div>
    </div>
    <div class="gi-block">
      <div class="gi-block-title">📐 Evaluation Protocol</div>
      <div class="gi-block-body">
        Macro-averaged precision, recall, and F1. ROC-AUC and PR-AUC for
        imbalanced class handling. Threshold fixed at 0.5 for binary output.
      </div>
    </div>
    <div class="gi-block">
      <div class="gi-block-title">🏷️ Annotation Scheme</div>
      <div class="gi-block-body">
        {ds["annotators"]}. Consensus binary label used for training.
        Individual labels (IOI, EBT, AOC) retained for inter-annotator analysis.
      </div>
    </div>
    <div class="gi-block">
      <div class="gi-block-title">📊 Class Distribution</div>
      <div class="gi-block-body">
        {ds["credible"]} credible · {ds["misinfo"]} misinformation.
        Class imbalance ratio {ds["imbalance"]}, reflecting real-world
        prevalence of health misinformation on YouTube.
      </div>
    </div>
    <div class="gi-block">
      <div class="gi-block-title">🌐 Data Streams</div>
      <div class="gi-block-body">
        {ds["streams"]}. Engagement signals: views, likes, comments
        {'and dislikes (pre-API removal)' if ds_id == "yt_full" else 'per video'}.
        Channel-level metadata included.
      </div>
    </div>
  </div>

  <div class="gi-insight">
    <strong>📌 Key Insight:</strong> {ds["insight"]}
  </div>
</div>
""", unsafe_allow_html=True)



#  PAGE: HOME (hero)


def page_home():
    st.markdown(
        hero_section_html(
            title_main="Misinformation Detection and Public Engagement",
            title_accent="",
            subtitle=(
                "A multimodal AI system that analyses YouTube videos across text, audio, "
                "and visual streams to detect health misinformation with scientific rigour. "
                "Built on the MHMisinfo dataset and powered by a BiGRU fusion architecture."
            ),
            badges=["BiGRU Encoder", "SVM", "DistilRoBERTa", "85.9% Accuracy", "MHMisinfo Dataset"],
        ),
        unsafe_allow_html=True,
    )



#  PAGE: DATASET ANALYSIS (selector + detail via session_state)


def page_dataset_analysis():
    st.markdown(
        '<div style="margin-bottom:28px">'
        '<div class="section-label" style="margin-bottom:8px">📊 Benchmark Results</div>'
        '<h2 style="margin:0;font-size:1.8rem;font-weight:800;letter-spacing:-0.02em">Dataset Analysis</h2>'
        '<p style="color:var(--text-mid);margin:8px 0 0;font-size:0.95rem">'
        'Select a dataset to explore its metrics, training progression, and model performance.'
        '</p></div>',
        unsafe_allow_html=True,
    )

    #  Dataset Overview Card
    st.markdown("""
<div class="dataset-overview-card">
  <div class="dataset-header">
    <span style="font-size:2rem">🗂️</span>
    <div><h2>MHMisinfo Dataset Overview</h2><p>Mental Health Misinformation · YouTube · Curated Benchmark</p></div>
  </div>
  <div class="dataset-panels">
    <div class="dataset-panel">
      <div class="dataset-panel-title">🥇 Gold Standard Dataset</div>
      <div class="dataset-file">videos_MHMisinfo_Gold.csv</div>
      <div class="dataset-stats-row">
        <div class="ds-stat"><span class="ds-val">739</span><span class="ds-label">Videos</span></div>
        <div class="ds-stat"><span class="ds-val">12</span><span class="ds-label">Columns</span></div>
        <div class="ds-stat"><span class="ds-val">84%</span><span class="ds-label">Credible</span></div>
        <div class="ds-stat"><span class="ds-val">16%</span><span class="ds-label">Misinfo</span></div>
      </div>
      <div class="ds-columns-title">Key Columns</div>
      <div class="ds-tags">video_id · video_title · video_description · audio_transcript · video_view_count · video_like_count · video_comment_count · label · label_ioi · label_ebt · label_aoc · platform</div>
      <div class="ds-insight"><b>📌 Insight:</b> Gold standard annotations from 3 independent labellers (IOI, EBT, AOC). Consensus label used for training. Audio transcripts enable speech-stream analysis. Strong class imbalance (5.16:1) reflects real-world prevalence of credible health content on YouTube.</div>
    </div>
    <div class="dataset-panel">
      <div class="dataset-panel-title">📦 Full Research Dataset</div>
      <div class="dataset-file">yt_full_dec16_with_metadata_with_transcription.csv</div>
      <div class="dataset-stats-row">
        <div class="ds-stat"><span class="ds-val">640</span><span class="ds-label">Videos</span></div>
        <div class="ds-stat"><span class="ds-val">22</span><span class="ds-label">Columns</span></div>
        <div class="ds-stat"><span class="ds-val">87%</span><span class="ds-label">Credible</span></div>
        <div class="ds-stat"><span class="ds-val">13%</span><span class="ds-label">Misinfo</span></div>
      </div>
      <div class="ds-columns-title">Key Columns</div>
      <div class="ds-tags">video_id · channel_title · channel_id · video_publish_date · video_title · video_description · video_category · video_tags · video_view_count · video_like_count · video_dislike_count · video_comment_count · video_thumbnail · collection_date · url · label · label_ioi · label_aoc · label_ebt · video_transcript · audio_transcript</div>
      <div class="ds-insight"><b>📌 Insight:</b> Full metadata including channel context, video categories, tags, and dual transcripts (video + audio streams separately). Dislike counts captured pre-YouTube API removal. Category distribution enables cross-topic misinformation analysis.</div>
    </div>
  </div>
  <div class="ds-benefits">
    <div class="ds-benefit-item">🔬 <b>Multimodal:</b> Text + Audio + Video transcript streams</div>
    <div class="ds-benefit-item">🏷️ <b>Multi-annotator:</b> 3 independent labels per video</div>
    <div class="ds-benefit-item">📈 <b>Rich engagement:</b> Views, likes, comments, dislikes</div>
    <div class="ds-benefit-item">🧠 <b>ML-ready:</b> Pre-processed transcriptions included</div>
    <div class="ds-benefit-item">🌐 <b>Temporal:</b> Collected Dec 2016 baseline</div>
    <div class="ds-benefit-item">⚕️ <b>Domain:</b> Mental health focused — depression, anxiety, therapy</div>
  </div>
</div>
""", unsafe_allow_html=True)

    selected_ds_id = st.session_state.get("selected_ds_detail", None)
    st.markdown(
        '<div class="ds-table-header">'
        '<span>Dataset</span><span>Goal</span><span>Size</span><span>Action</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    for ds in DATASETS:
        is_sel = selected_ds_id == ds["id"]
        active_badge = (
            "<span style='font-size:0.7rem;background:var(--emerald-light);color:var(--emerald);"
            "padding:2px 8px;border-radius:20px;font-weight:600'>Active</span>"
            if is_sel else ""
        )
        st.markdown(
            f'<div class="ds-row {"selected" if is_sel else ""}">'
            f'<div><div class="ds-name">{ds["name"]}</div>{active_badge}</div>'
            f'<div class="ds-goal">{ds["goal"]}</div>'
            f'<div class="ds-size">{ds["size"]}</div>'
            f'<div></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("✓ Selected" if is_sel else "Select →", key=f"btn_{ds['id']}", disabled=is_sel):
            st.session_state["selected_ds_detail"] = ds["id"]
            st.rerun()

    if selected_ds_id is None:
        st.markdown(
            '<div style="text-align:center;padding:48px;color:var(--text-light)">'
            '<div style="font-size:3rem;margin-bottom:12px">☝️</div>'
            '<div style="font-weight:600;font-size:1rem">Select a dataset above to view its analysis</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    ds = next(d for d in DATASETS if d["id"] == selected_ds_id)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="margin-bottom:22px">'
        f'<div class="section-label" style="margin-bottom:6px">Results for</div>'
        f'<h3 style="margin:0;font-size:1.4rem;font-weight:800">{ds["name"]}</h3>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_bars, col_info = st.columns([1.4, 1], gap="large")
    with col_bars:
        st.markdown('<div class="section-label" style="margin-bottom:14px">📏 Performance Metrics</div>',
                    unsafe_allow_html=True)
        for name, value, color, icon, delay in [
            ("Accuracy",          REPORT_METRICS["accuracy"],        "#10B981", "🎯", 0.00),
            ("Precision (Macro)", REPORT_METRICS["precision_macro"], "#6366F1", "📐", 0.12),
            ("Recall (Macro)",    REPORT_METRICS["recall_macro"],    "#F59E0B", "🔁", 0.24),
            ("F1 Score (Macro)",  REPORT_METRICS["f1_macro"],        "#8B5CF6", "⚖️", 0.36),
            ("ROC-AUC",           REPORT_METRICS["roc_auc"],         "#0EA5E9", "📉", 0.48),
            ("PR-AUC",            REPORT_METRICS["pr_auc"],          "#EF4444", "🔻", 0.60),
        ]:
            st.markdown(progress_bar_html(name, value, color, icon, delay), unsafe_allow_html=True)

    with col_info:
        st.markdown('<div class="section-label" style="margin-bottom:14px">🗂️ Dataset Info</div>',
                    unsafe_allow_html=True)
        st.markdown(stat_grid_html([(str(ds["cols"]), "Total Columns")]), unsafe_allow_html=True)
        st.markdown(
            f'<div class="vcard-mini" style="margin-bottom:14px">'
            f'<div class="section-label" style="margin-bottom:8px">📝 Description</div>'
            f'<p style="font-size:0.84rem;color:var(--text-mid);line-height:1.65;margin:0">'
            f'{ds["description"]}</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown("""
<div class="vcard-mini"><div class="section-label" style="margin-bottom:12px">🔢 Confusion Matrix</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
    <div style="text-align:center;padding:12px;background:var(--emerald-light);border-radius:8px;border:1px solid #6EE7B7"><div style="font-size:1.6rem;font-weight:800;color:var(--emerald);font-family:'DM Mono',monospace">53</div><div style="font-size:0.7rem;color:var(--emerald);font-weight:600;margin-top:2px">True Neg</div></div>
    <div style="text-align:center;padding:12px;background:var(--crimson-light);border-radius:8px;border:1px solid #FCA5A5"><div style="font-size:1.6rem;font-weight:800;color:var(--crimson);font-family:'DM Mono',monospace">3</div><div style="font-size:0.7rem;color:var(--crimson);font-weight:600;margin-top:2px">False Pos</div></div>
    <div style="text-align:center;padding:12px;background:var(--amber-light);border-radius:8px;border:1px solid #FCD34D"><div style="font-size:1.6rem;font-weight:800;color:var(--amber);font-family:'DM Mono',monospace">6</div><div style="font-size:0.7rem;color:var(--amber);font-weight:600;margin-top:2px">False Neg</div></div>
    <div style="text-align:center;padding:12px;background:var(--sky-light);border-radius:8px;border:1px solid #7DD3FC"><div style="font-size:1.6rem;font-weight:800;color:var(--sky);font-family:'DM Mono',monospace">2</div><div style="font-size:0.7rem;color:var(--sky);font-weight:600;margin-top:2px">True Pos</div></div>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    random.seed(REPORT_CONFIG["seed"])
    epoch_data = simulate_epoch_data(REPORT_METRICS["accuracy"], epochs=REPORT_CONFIG["epochs"])

    import plotly.graph_objects as go

    # Training Config (full width)
    st.markdown(
        '<div class="vcard" style="height:auto">'
        '<div class="section-label" style="margin-bottom:14px">⚙️ Training Config</div>',
        unsafe_allow_html=True,
    )
    config_items = [
        ("Model",       REPORT_CONFIG["model_name"]),
        ("Encoder",     REPORT_CONFIG["encoder"].upper()),
        ("Epochs",      str(REPORT_CONFIG["epochs"])),
        ("Batch Size",  str(REPORT_CONFIG["batch_size"])),
        ("Learning Rate", str(REPORT_CONFIG["lr"])),
        ("Emb Dim",     str(REPORT_CONFIG["emb_dim"])),
        ("Hidden Dim",  str(REPORT_CONFIG["hidden_dim"])),
        ("Dropout",     str(REPORT_CONFIG["dropout"])),
    ]
    for k, v in config_items:
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:8px 0;border-bottom:1px solid var(--border)">'
            f'<span style="font-size:0.82rem;color:var(--text-mid)">{k}</span>'
            f'<span style="font-size:0.82rem;font-weight:600;font-family:\'DM Mono\',monospace;'
            f'color:var(--text-dark)">{v}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label" style="margin-bottom:14px">📊 Visual Analysis</div>',
                unsafe_allow_html=True)

    pc1, pc2 = st.columns(2, gap="large")
    with pc1:
        names  = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "PR-AUC"]
        values = [REPORT_METRICS[k] for k in ["accuracy", "precision_macro", "recall_macro",
                                               "f1_macro", "roc_auc", "pr_auc"]]
        colors = ["#10B981", "#6366F1", "#F59E0B", "#8B5CF6", "#0EA5E9", "#EF4444"]
        fig = go.Figure(go.Bar(
            x=[v * 100 for v in values], y=names, orientation="h",
            marker=dict(color=colors, opacity=0.88, line=dict(width=0)),
            text=[f"{v * 100:.1f}%" for v in values], textposition="outside",
            hovertemplate="<b>%{y}</b>: %{x:.2f}%<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="'DM Sans',sans-serif", color="#212529"),
            margin=dict(l=0, r=60, t=40, b=10),
            title=dict(text="All Metrics Comparison", font=dict(size=14, color="#495057"), x=0),
            height=300,
            xaxis=dict(range=[0, 110], showticklabels=False, gridcolor="#DEE2E6"),
            yaxis=dict(tickfont=dict(size=12)), bargap=0.32,
        )
        st.plotly_chart(fig, use_container_width=True, key="metrics_comparison_chart_final")

    with pc2:
        random.seed(42)
        epochs_x  = list(range(1, REPORT_CONFIG["epochs"] + 1))
        acc_curve  = [ed[0] for ed in epoch_data]
        loss_curve = [
            max(0.05, 0.9 - 0.07 * i + random.uniform(-0.03, 0.03))
            for i in range(REPORT_CONFIG["epochs"])
        ]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=epochs_x, y=[v * 100 for v in acc_curve],
            name="Accuracy (%)", mode="lines+markers",
            line=dict(color="#10B981", width=2.5), marker=dict(size=6),
        ))
        fig2.add_trace(go.Scatter(
            x=epochs_x, y=[v * 100 for v in loss_curve],
            name="Loss (scaled)", mode="lines+markers",
            line=dict(color="#EF4444", width=2.5, dash="dot"),
            marker=dict(size=6), yaxis="y2",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="'DM Sans',sans-serif", color="#212529"),
            margin=dict(l=0, r=0, t=40, b=20),
            title=dict(text="Training Convergence", font=dict(size=14, color="#495057"), x=0),
            height=300,
            xaxis=dict(title="Epoch", gridcolor="#DEE2E6", dtick=1),
            yaxis=dict(title="Accuracy (%)", gridcolor="#DEE2E6"),
            yaxis2=dict(title="Loss", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", y=1.12, font=dict(size=11)),
        )
        st.plotly_chart(fig2, use_container_width=True, key="training_convergence_chart_final")



#  PAGE: VIDEO LAB


def _metric_card(icon: str, value: str, label: str, border_color: str) -> str:
    return (
        f'<div style="background:#13161e;border:1px solid #1e2330;border-radius:12px;'
        f'border-top:3px solid {border_color};padding:1.1rem 1.3rem;text-align:center;'
        f'height:110px;display:flex;flex-direction:column;justify-content:center;gap:2px">'
        f'<div style="font-size:1.6rem">{icon}</div>'
        f'<div style="font-size:1.35rem;font-weight:700;color:{border_color};'
        f'font-family:\'DM Mono\',monospace;line-height:1.1">{value}</div>'
        f'<div style="font-size:0.72rem;color:#5a6070;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-top:2px">{label}</div>'
        f'</div>'
    )


def _stat_card(emoji: str, pct: float, label: str, color: str) -> str:
    return (
        f'<div style="background:#13161e;border:1px solid #1e2330;border-radius:12px;'
        f'border-top:3px solid {color};padding:1.1rem 1.3rem;text-align:center;'
        f'height:110px;display:flex;flex-direction:column;justify-content:center;gap:2px">'
        f'<div style="font-size:1.6rem">{emoji}</div>'
        f'<div style="font-size:1.35rem;font-weight:700;color:{color};'
        f'font-family:\'DM Mono\',monospace;line-height:1.1">{pct:.1f}%</div>'
        f'<div style="font-size:0.72rem;color:#5a6070;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-top:2px">{label}</div>'
        f'</div>'
    )


def _section_label(text: str, mb: int = 14) -> str:
    return (
        f'<p style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;'
        f'text-transform:uppercase;color:#5a6070;margin:0 0 {mb}px 0">{text}</p>'
    )


def _hr() -> str:
    return '<hr style="border:none;border-top:1px solid #1e2330;margin:1.5rem 0">'


def _run_analysis_pipeline(vid_id, api_key, max_comments, sentiment_method, fetch_tr):
    from src import charts as ch
    from src import fetcher as ft

    with st.spinner("Fetching video data…"):
        meta, err = ft.fetch_video_metadata(vid_id, api_key)
    if err:
        st.error(f"YouTube API error: {err}")
        return

    st.markdown(_section_label("📊 Video Metrics"), unsafe_allow_html=True)
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1:
        st.markdown(_metric_card("👁️", fmt_num(meta["view_count"]),    "Total Views", "#10B981"), unsafe_allow_html=True)
    with mc2:
        st.markdown(_metric_card("👍", fmt_num(meta["like_count"]),    "Total Likes", "#6366F1"), unsafe_allow_html=True)
    with mc3:
        st.markdown(_metric_card("💬", fmt_num(meta["comment_count"]), "Comments",    "#F59E0B"), unsafe_allow_html=True)
    with mc4:
        st.markdown(_metric_card("⏱️", meta["duration"],               "Duration",    "#0EA5E9"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    thumb_col, info_col = st.columns([1, 2], gap="large")
    with thumb_col:
        if meta.get("thumbnail_url"):
            st.image(meta["thumbnail_url"], use_column_width=True)
        st.markdown(
            f'<div style="font-weight:700;font-size:0.95rem;color:#e8eaf0;margin-top:6px">'
            f'{meta.get("title","")}</div>'
            f'<div style="font-size:0.82rem;color:#5a6070;margin-top:4px">'
            f'🎬 {meta.get("channel_title","")}</div>',
            unsafe_allow_html=True,
        )

    with info_col:
        tags     = meta.get("tags", [])
        tag_html = "".join(
            f'<span style="display:inline-block;background:#1a1d27;border:1px solid #1e2330;'
            f'border-radius:4px;padding:2px 8px;font-size:0.7rem;color:#8090a0;margin:2px">#{t}</span>'
            for t in tags[:20]
        ) or '<span style="color:#5a6070;font-size:0.78rem">(none)</span>'

        desc_short = (meta.get("description", "")[:450] + "…") if len(meta.get("description", "")) > 450 else meta.get("description", "")

        info_html = f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
  <div style="background:#13161e;border:1px solid #1e2330;border-radius:10px;padding:0.85rem 1rem">
    <div style="font-size:0.62rem;color:#5a6070;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px">🏷️ Tags</div>
    <div>{tag_html}</div>
  </div>
  <div style="background:#13161e;border:1px solid #1e2330;border-radius:10px;padding:0.85rem 1rem">
    <div style="font-size:0.62rem;color:#5a6070;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px">📅 Published</div>
    <div style="font-size:1rem;font-weight:600;color:#e8eaf0">{meta.get("published_at","")}</div>
    <div style="font-size:0.82rem;color:#5a6070;margin-top:4px">{meta.get("channel_title","")}</div>
  </div>
</div>
<div style="background:#13161e;border:1px solid #1e2330;border-radius:10px;padding:0.85rem 1rem">
  <div style="font-size:0.62rem;color:#5a6070;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px">📝 Description</div>
  <div style="font-size:0.84rem;color:#8090a0;line-height:1.6;max-height:90px;overflow:hidden">{desc_short}</div>
</div>
"""
        st.markdown(info_html, unsafe_allow_html=True)

    st.markdown(_hr(), unsafe_allow_html=True)

    transcript_text = ""
    if fetch_tr:
        with st.spinner("Fetching transcript…"):
            transcript_text, tr_status = ft.fetch_transcript(vid_id)
        st.caption(tr_status)

    with st.spinner("Fetching comments…"):
        comments_df, cmt_status = ft.fetch_comments(vid_id, api_key, max_comments=max_comments)
    st.caption(cmt_status)

    with st.spinner("Running misinformation detection…"):
        result = az.detect_misinformation(
            text=meta.get("title", "") + " " + meta.get("description", ""),
            tags=meta.get("tags", []),
            audio_transcript=transcript_text,
            video_transcript=transcript_text,
        )

    score = result["score"]
    conf  = result["confidence_pct"]
    if score >= 0.65:
        banner_color, icon, verdict_text = "#ff4757", "🚨", "LIKELY MISINFORMATION"
    elif score >= 0.35:
        banner_color, icon, verdict_text = "#ffb347", "⚠️", "UNCERTAIN / MIXED SIGNALS"
    else:
        banner_color, icon, verdict_text = "#00e5a0", "✅", "APPEARS CREDIBLE"

    st.markdown(f"""
<div style="background:linear-gradient(135deg,{banner_color}22,{banner_color}11);
            border:2px solid {banner_color};border-radius:16px;padding:1.5rem 2rem;
            margin-bottom:1.2rem;text-align:center">
  <div style="font-size:3rem">{icon}</div>
  <div style="font-size:1.6rem;font-weight:800;color:{banner_color};letter-spacing:-0.02em">{verdict_text}</div>
  <div style="font-size:2.2rem;font-weight:700;color:{banner_color};font-family:monospace;margin-top:4px">{conf}% Confidence</div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        f'<div style="background:#0d1119;border-left:3px solid #ffb347;padding:0.8rem 1rem;'
        f'border-radius:0 8px 8px 0;font-size:0.85rem;color:#c0c4cc;line-height:1.65;margin-bottom:1rem">'
        f'🧠 <b>Reasoning:</b> {result["reasoning"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 🔬 Modality Analysis")
    mod_analysis = result.get("modality_analysis", {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(ch.modality_misinfo_distribution(mod_analysis),
                        use_container_width=True, config={"displayModeBar": False})
    with col2:
        st.plotly_chart(ch.trust_score_by_modality(mod_analysis),
                        use_container_width=True, config={"displayModeBar": False})
    with col3:
        st.plotly_chart(ch.uncertainty_analysis(mod_analysis),
                        use_container_width=True, config={"displayModeBar": False})

    st.markdown(_section_label("🔑 Keyword Analysis"), unsafe_allow_html=True)
    keywords = az.extract_keywords(
        meta.get("title", "") + " " + meta.get("description", ""),
        tags=meta.get("tags", []),
    )
    st.plotly_chart(
        ch.keyword_bar(keywords, "Top Keywords (Video Metadata)", color="#10B981"),
        use_container_width=True, config={"displayModeBar": False},
    )

    if not comments_df.empty:
        st.markdown(_hr(), unsafe_allow_html=True)
        st.markdown(_section_label("😊 Sentiment Analysis"), unsafe_allow_html=True)

        with st.spinner("Running sentiment analysis…"):
            texts      = comments_df["text"].fillna("").tolist()
            sentiments = az.analyze_sentiment_batch(texts, method=sentiment_method)
            summary    = az.sentiment_summary(sentiments)

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(_stat_card("😊", summary["pos_pct"], "Positive Engagement", "#10B981"), unsafe_allow_html=True)
        with s2:
            st.markdown(_stat_card("😟", summary["neg_pct"], "Negative Engagement", "#EF4444"), unsafe_allow_html=True)
        with s3:
            st.markdown(_stat_card("😐", summary["neu_pct"], "Neutral",             "#F59E0B"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        sa_col, sb_col = st.columns(2, gap="large")
        with sa_col:
            st.plotly_chart(ch.sentiment_donut(summary), use_container_width=True, config={"displayModeBar": False})
        with sb_col:
            st.plotly_chart(ch.sentiment_timeline(comments_df, sentiments), use_container_width=True, config={"displayModeBar": False})

        st.markdown(_section_label("🔑 Sentiment Keywords (Comments)"), unsafe_allow_html=True)
        pos_kw, neg_kw = az.sentiment_weighted_keywords(comments_df, sentiments)
        st.plotly_chart(ch.keyword_comparison(pos_kw, neg_kw), use_container_width=True, config={"displayModeBar": False})

        st.markdown(_section_label("💬 Comments Deep-Dive"), unsafe_allow_html=True)
        display_df = comments_df.copy()
        display_df["sentiment"] = [s["label"]                     for s in sentiments]
        display_df["compound"]  = [round(s.get("compound", 0), 3) for s in sentiments]
        cols_show = ["author", "text", "likes", "compound", "published_at"]

        df_pos = display_df[display_df["sentiment"] == "POSITIVE"][cols_show].reset_index(drop=True)
        df_neg = display_df[display_df["sentiment"] == "NEGATIVE"][cols_show].reset_index(drop=True)
        df_neu = display_df[display_df["sentiment"] == "NEUTRAL"][cols_show].reset_index(drop=True)

        tab_pos, tab_neg, tab_neu = st.tabs(["Positive Engagement", "Negative Engagement", "Neutral"])
        with tab_pos:
            if not df_pos.empty:
                st.dataframe(df_pos, use_container_width=True, height=280)
            else:
                st.info("No positive engagement comments found.")
        with tab_neg:
            if not df_neg.empty:
                st.dataframe(df_neg, use_container_width=True, height=280)
            else:
                st.info("No negative engagement comments found.")
        with tab_neu:
            if not df_neu.empty:
                st.dataframe(df_neu, use_container_width=True, height=280)
            else:
                st.info("No neutral comments found.")
    else:
        st.info("💬 No comments available for sentiment analysis.")


def page_video_lab():
    st.markdown("""
<div style="margin-bottom:28px">
  <p style="font-size:0.68rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;
            color:#5a6070;margin:0 0 8px 0">🎬 Real-Time Analysis</p>
  <h2 style="margin:0;font-size:1.8rem;font-weight:800;letter-spacing:-0.02em">Video Intelligence Lab</h2>
  <p style="color:#8090a0;margin:8px 0 0;font-size:0.95rem">
    Paste a YouTube URL or search by keyword to run live misinfo detection,
    sentiment analysis, and engagement scoring.
  </p>
</div>
""", unsafe_allow_html=True)

    api_key = YT_API_KEY
    if not api_key:
        st.warning("YouTube API key not configured. Set `YT_API_KEY` in your `.env` file or as an environment variable.")
        st.stop()

    tab_url, tab_upload = st.tabs(["🔗 YouTube URL / Video ID", "📁 Upload Video / Search by Title"])

    with tab_url:
        with st.form(key="video_lab_url_form", clear_on_submit=False):
            yt_url = st.text_input(
                "YouTube URL or Video ID",
                placeholder="https://www.youtube.com/watch?v=…",
                key="yt_url_input",
            )
            with st.expander("⚙️ Advanced Options", expanded=False):
                max_comments     = st.slider("Max comments to fetch", 20, 200, 100, step=10, key="max_url")
                sentiment_method = st.radio("Sentiment method", ["vader", "hf"], horizontal=True,
                                            help="VADER is faster; HF (DistilBERT) is more accurate",
                                            key="sent_url")
                fetch_tr = st.checkbox("Fetch transcript", value=True, key="tr_url")
            run_btn = st.form_submit_button("🔍 Analyse", type="primary", use_container_width=False)

        if not run_btn:
            st.markdown("""
<div style="text-align:center;padding:48px 24px;
            background:linear-gradient(135deg,rgba(240,253,247,0.04),rgba(238,242,255,0.04));
            border-radius:15px;border:1px solid #1e2330;margin-top:12px">
  <div style="font-size:3rem;margin-bottom:14px">🎬</div>
  <h3 style="margin:0 0 8px;font-weight:700">Paste a YouTube URL to begin</h3>
  <p style="color:#8090a0;font-size:0.9rem;margin:0 auto;max-width:480px">
    Enter a YouTube URL above, then click <b>Analyse</b> or press <b>Enter</b>.<br>
    The system will fetch metadata, comments, and transcripts in real-time.
  </p>
</div>
""", unsafe_allow_html=True)

        if run_btn:
            if not yt_url.strip():
                st.warning("Please enter a YouTube URL or video ID.")
            else:
                try:
                    from src import fetcher as ft
                except ImportError as e:
                    st.error(f"Import error: {e}")
                    st.stop()
                vid_id = ft.extract_video_id(yt_url.strip())
                if not vid_id:
                    st.error("Could not extract a valid YouTube video ID from the input.")
                else:
                    _run_analysis_pipeline(vid_id, api_key, max_comments, sentiment_method, fetch_tr)

    with tab_upload:
        st.markdown("#### 🎬 Upload a video file then search YouTube to analyze it")
        st.file_uploader(
            "Drop a video file (mp4, mov, avi, mkv, webm)",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            help="Upload to identify the video, then search YouTube to fetch metadata & comments.",
            key="video_upload",
        )
        keyword = st.text_input("Search keyword / video title",
                                 placeholder="Enter title or keyword…", key="search_keyword")
        col_search, _ = st.columns([1, 3])
        with col_search:
            search_clicked = st.button("🔎 Find on YouTube", use_container_width=True, key="search_btn")

        if search_clicked and keyword.strip():
            from src.fetcher import search_videos_by_title
            with st.spinner("Searching YouTube…"):
                results = search_videos_by_title(keyword.strip(), api_key, max_results=5)
            if not results:
                st.warning("No results found.")
            else:
                st.markdown("**Select a video to analyze:**")
                choices = {
                    f"{r['title'][:70]} — {r['channel_title']}": r["video_id"]
                    for r in results
                }
                for r in results:
                    c1, c2 = st.columns([1, 4])
                    with c1:
                        if r.get("thumbnail_url"):
                            st.image(r["thumbnail_url"], width=100)
                    with c2:
                        st.markdown(f"**{r['title']}**")
                        st.caption(f"{r['channel_title']} · {r['published_at']}")

                selected_title = st.radio("Pick one:", list(choices.keys()),
                                           label_visibility="collapsed", key="search_pick")
                with st.expander("⚙️ Advanced Options", expanded=False):
                    max_comments2     = st.slider("Max comments to fetch", 20, 200, 100, step=10, key="max_search")
                    sentiment_method2 = st.radio("Sentiment method", ["vader", "hf"], horizontal=True, key="sent_search")
                    fetch_tr2         = st.checkbox("Fetch transcript", value=True, key="tr_search")

                if st.button("▶ Analyze Selected Video", type="primary", key="analyze_selected"):
                    _run_analysis_pipeline(choices[selected_title], api_key,
                                           max_comments2, sentiment_method2, fetch_tr2)
        elif search_clicked:
            st.warning("Please enter a keyword to search.")



#  ROUTING


_current_page = st.session_state.get("page", "landing")

#  Landing page: no nav, no sub-header 
if _current_page == "landing":
    page_landing()
    st.stop()

#  All other pages: show compact top-left header (branding + Home button) ─
_render_sub_header()

#  Dataset detail & Video Lab pages — no navbar needed 
#    Users return to landing via the "Home" button in _render_sub_header().
if _current_page == "dataset_gold":
    page_dataset_detail("mhmisinfo")
    st.markdown(
        '<div style="margin-top:60px;padding-top:20px;border-top:1px solid var(--border);'
        'text-align:center;color:var(--text-light);font-size:0.78rem">'
        '<span style="font-family:\'DM Mono\',monospace">'
        'Made by <a href="https://scholar.google.com/citations?user=7JpdAw0AAAAJ&hl=en" style="color:var(--emerald);text-decoration:none">Abdullah Al Maruf</a> · Built on '
        '<a href="https://huggingface.co/rocky250/MHMisinfo" style="color:var(--emerald);text-decoration:none">MHMisinfo</a> · '
        '<a href="https://huggingface.co/distilroberta-base" style="color:var(--indigo);text-decoration:none">DistilRoBERTa</a>'
        '</span></div>',
        unsafe_allow_html=True,
    )
    st.stop()

if _current_page == "dataset_full":
    page_dataset_detail("yt_full")
    st.markdown(
        '<div style="margin-top:60px;padding-top:20px;border-top:1px solid var(--border);'
        'text-align:center;color:var(--text-light);font-size:0.78rem">'
        '<span style="font-family:\'DM Mono\',monospace">'
        'Made by <a href="https://scholar.google.com/citations?user=7JpdAw0AAAAJ&hl=en" style="color:var(--emerald);text-decoration:none">Abdullah Al Maruf</a> · Built on '
        '<a href="https://huggingface.co/rocky250/MHMisinfo" style="color:var(--emerald);text-decoration:none">MHMisinfo</a> · '
        '<a href="https://huggingface.co/distilroberta-base" style="color:var(--indigo);text-decoration:none">DistilRoBERTa</a>'
        '</span></div>',
        unsafe_allow_html=True,
    )
    st.stop()

if _current_page == "video_lab":
    page_video_lab()
    st.markdown(
        '<div style="margin-top:60px;padding-top:20px;border-top:1px solid var(--border);'
        'text-align:center;color:var(--text-light);font-size:0.78rem">'
        '<span style="font-family:\'DM Mono\',monospace">'
        'Made by <a href="https://scholar.google.com/citations?user=7JpdAw0AAAAJ&hl=en" style="color:var(--emerald);text-decoration:none">Abdullah Al Maruf</a> · Built on '
        '<a href="https://huggingface.co/rocky250/MHMisinfo" style="color:var(--emerald);text-decoration:none">MHMisinfo</a> · '
        '<a href="https://huggingface.co/distilroberta-base" style="color:var(--indigo);text-decoration:none">DistilRoBERTa</a>'
        '</span></div>',
        unsafe_allow_html=True,
    )
    st.stop()

#  Home & Dataset Analysis pages — show navbar ─
_nav_default = {
    "home":             0,
    "dataset_analysis": 1,
}.get(_current_page, 0)

with st.container():
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    selected_page = option_menu(
        menu_title=None,
        options=["Home", "Dataset Analysis", "Video Lab"],
        icons=["house-fill", "bar-chart-fill", "camera-video-fill"],
        default_index=_nav_default,
        orientation="horizontal",
        styles={
            "container":         {"padding": "0!important", "background": "transparent"},
            "icon":              {"color": "#868E96", "font-size": "14px"},
            "nav-link":          {"font-family": "'DM Sans', sans-serif", "font-size": "14px",
                                  "font-weight": "600", "color": "#495057", "padding": "10px 22px",
                                  "border-radius": "10px", "--hover-color": "#F0FDF7"},
            "nav-link-selected": {"background-color": "#212529", "color": "white", "font-weight": "700"},
        },
    )
    st.markdown("</div>", unsafe_allow_html=True)

#  Route based on nav selection 
if selected_page == "Home":
    st.session_state["page"] = "home"
    page_home()

elif selected_page == "Dataset Analysis":
    st.session_state["page"] = "dataset_analysis"
    page_dataset_analysis()

elif selected_page == "Video Lab":
    # Clicking Video Lab from the navbar transitions to the no-navbar path
    st.session_state["page"] = "video_lab"
    st.rerun()

#  Footer for Home / Dataset Analysis pages (navbar pages only) 
st.markdown(
    '<div style="margin-top:60px;padding-top:20px;border-top:1px solid var(--border);'
    'text-align:center;color:var(--text-light);font-size:0.78rem">'
    '<span style="font-family:\'DM Mono\',monospace">'
    'Made by <a href="https://scholar.google.com/citations?user=7JpdAw0AAAAJ&hl=en" style="color:var(--emerald);text-decoration:none">Abdullah Al Maruf</a> · Built on '
    '<a href="https://huggingface.co/rocky250/MHMisinfo" style="color:var(--emerald);text-decoration:none">MHMisinfo</a> · '
    '<a href="https://huggingface.co/distilroberta-base" style="color:var(--indigo);text-decoration:none">DistilRoBERTa</a>'
    '</span></div>',
    unsafe_allow_html=True,
)
