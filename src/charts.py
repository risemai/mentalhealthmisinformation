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
