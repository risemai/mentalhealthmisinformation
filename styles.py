"""
styles.py — Global CSS definitions for Veritas Analytics App.
"""


def get_global_css() -> str:
    return """
<style>
/* 
   FONTS
 */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@700;800&display=swap');

/* 
   ROOT VARIABLES
 */
:root {
    --bg-main:      #F8F9FA;
    --bg-white:     #FFFFFF;
    --bg-soft:      #F0F2F5;
    --text-dark:    #212529;
    --text-mid:     #495057;
    --text-light:   #868E96;
    --border:       #DEE2E6;
    --shadow-sm:    0 2px 8px rgba(0,0,0,0.06);
    --shadow-md:    0 4px 20px rgba(0,0,0,0.08);
    --shadow-lg:    0 8px 40px rgba(0,0,0,0.12);
    --radius-sm:    8px;
    --radius-md:    15px;
    --radius-lg:    24px;
    /* accent palette */
    --emerald:      #10B981;
    --emerald-light:#D1FAE5;
    --amber:        #F59E0B;
    --amber-light:  #FEF3C7;
    --indigo:       #6366F1;
    --indigo-light: #EEF2FF;
    --crimson:      #EF4444;
    --crimson-light:#FEE2E2;
    --sky:          #0EA5E9;
    --sky-light:    #E0F2FE;
    --violet:       #8B5CF6;
    --violet-light: #EDE9FE;
}

/* 
   BASE & RESET
 */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-main) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-dark) !important;
}

/* ── Nuke Streamlit's native toolbar / header bar entirely ─────────────── */
[data-testid="stHeader"],
[data-testid="stHeader"] * {
    display:    none       !important;
    height:     0px        !important;
    min-height: 0px        !important;
    max-height: 0px        !important;
    padding:    0          !important;
    margin:     0          !important;
    overflow:   hidden     !important;
    visibility: hidden     !important;
}

/* Fill whatever pixel-gap the header skeleton still occupies ────────────
   If Streamlit cannot fully collapse it, the gap will show as #C9E1C1
   instead of an ugly white stripe.                                        */
[data-testid="stApp"]::before,
[data-testid="stAppViewContainer"]::before {
    content:    '';
    display:    block;
    height:     0;
    background: #C9E1C1;
}

/* Ensure the outermost app wrapper itself starts at pixel 0 */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    margin-top:  0 !important;
    padding-top: 0 !important;
}

/* Remove ALL top padding from every variant of the main block-container */
.main .block-container,
[data-testid="block-container"],
[data-testid="stMainBlockContainer"],
section[data-testid="stMain"] > div,
section[data-testid="stMain"] > div.block-container {
    padding-top: 0 !important;
    margin-top:  0 !important;
}

[data-testid="stSidebar"] {
    background-color: var(--bg-white) !important;
    border-right: 1px solid var(--border) !important;
}

/* Hide default hamburger & deploy */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

/* 
   TYPOGRAPHY
 */
h1, h2, h3, h4 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-dark) !important;
    letter-spacing: -0.02em;
}

.display-title {
    font-family: 'Playfair Display', serif;
    font-weight: 800;
    font-size: clamp(2.4rem, 5vw, 3.6rem);
    color: var(--text-dark);
    line-height: 1.1;
    letter-spacing: -0.03em;
}

.display-title .accent {
    background: linear-gradient(135deg, var(--emerald), var(--sky));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-light);
}

/* 
   NAVBAR (streamlit-option-menu override)
 */
.nav-container {
    background: var(--bg-white);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    padding: 6px;
    margin-bottom: 28px;
    border: 1px solid var(--border);
}

/* 
   CARD COMPONENT  (generic .card  +  .vcard aliases)
 */
.card,
.vcard {
    background: var(--bg-white);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    padding: 24px 28px;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    height: 100%;
}

.card:hover,
.vcard:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

.vcard-mini {
    background: var(--bg-white);
    border-radius: var(--radius-sm);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    padding: 18px 20px;
}

/* 
   METRIC CARDS (Views, Likes, etc.)
 */
.metric-card {
    background: var(--bg-white);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}

.metric-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-3px);
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--bar-color, var(--emerald));
    border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.metric-card .metric-icon {
    font-size: 1.8rem;
    margin-bottom: 10px;
    display: block;
}

.metric-card .metric-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--text-dark);
    line-height: 1;
    margin-bottom: 4px;
    font-family: 'DM Mono', monospace;
}

.metric-card .metric-label {
    font-size: 0.78rem;
    color: var(--text-light);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'DM Mono', monospace;
}

.metric-card .metric-delta {
    position: absolute;
    top: 16px; right: 16px;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
}

.metric-card .metric-delta.up {
    background: var(--emerald-light);
    color: var(--emerald);
}

.metric-card .metric-delta.neutral {
    background: var(--sky-light);
    color: var(--sky);
}

/* 
   ANIMATED PROGRESS BARS
 */
.metric-bar-wrap {
    background: var(--bg-white);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    padding: 20px 24px;
    margin-bottom: 14px;
}

.metric-bar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.metric-bar-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text-dark);
    display: flex;
    align-items: center;
    gap: 8px;
}

.metric-bar-value {
    font-family: 'DM Mono', monospace;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-dark);
}

.bar-track {
    background: var(--bg-soft);
    border-radius: 100px;
    height: 10px;
    overflow: hidden;
    position: relative;
}

.bar-fill {
    height: 100%;
    border-radius: 100px;
    animation: barSlide 1.4s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    transform-origin: left;
    width: 0%;
}

@keyframes barSlide {
    0%   { width: 0%; opacity: 0.6; }
    60%  { opacity: 1; }
    100% { width: var(--target-width); opacity: 1; }
}

/* 
   DATASET TABLE
 */
.ds-table-header {
    display: grid;
    grid-template-columns: 2fr 3fr 1fr 1fr;
    gap: 12px;
    padding: 10px 20px;
    background: var(--bg-soft);
    border-radius: var(--radius-sm);
    margin-bottom: 8px;
}

.ds-table-header span {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-light);
    font-family: 'DM Mono', monospace;
}

.ds-row {
    display: grid;
    grid-template-columns: 2fr 3fr 1fr 1fr;
    gap: 12px;
    align-items: center;
    padding: 16px 20px;
    background: var(--bg-white);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    margin-bottom: 8px;
    transition: all 0.2s ease;
}

.ds-row:hover {
    border-color: var(--emerald);
    box-shadow: 0 0 0 3px var(--emerald-light);
}

.ds-row.selected {
    border-color: var(--emerald);
    background: #F0FDF7;
}

.ds-name {
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--text-dark);
}

.ds-goal {
    font-size: 0.82rem;
    color: var(--text-mid);
    line-height: 1.4;
}

.ds-size {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: var(--text-mid);
}

/* 
   EPOCH BARS
 */
.epoch-bar-container {
    background: var(--bg-white);
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    padding: 20px 24px;
}

.epoch-bar-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}

.epoch-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-light);
    min-width: 52px;
}

.epoch-track {
    flex: 1;
    background: var(--bg-soft);
    border-radius: 100px;
    height: 8px;
    overflow: hidden;
}

.epoch-fill {
    height: 100%;
    border-radius: 100px;
    animation: barSlide 1.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

.epoch-val {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    min-width: 44px;
    text-align: right;
}

/* 
   INFO STAT GRID  
 */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}

.stat-box {
    background: var(--bg-white);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 16px 18px;
    text-align: center;
    box-shadow: var(--shadow-sm);
}

.stat-box .stat-num {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-dark);
    font-family: 'DM Mono', monospace;
    display: block;
}

.stat-box .stat-desc {
    font-size: 0.75rem;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin-top: 4px;
    display: block;
}

/* 
   HERO SECTION
 */
.hero-section {
    background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF7 50%, #EEF2FF 100%);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    padding: 48px 52px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}

.hero-section::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(16,185,129,0.08), transparent 70%);
    border-radius: 50%;
}

/* 
   TAG CHIPS
 */
.tag-chip {
    display: inline-block;
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-mid);
    margin: 3px 3px 3px 0;
    transition: all 0.15s ease;
}

.tag-chip:hover {
    background: var(--emerald-light);
    border-color: var(--emerald);
    color: var(--emerald);
}

/* 
   CONFIDENCE BADGE
 */
.confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 100px;
    font-weight: 600;
    font-size: 0.84rem;
    font-family: 'DM Mono', monospace;
}

.confidence-badge.danger {
    background: var(--crimson-light);
    color: var(--crimson);
    border: 1px solid #FCA5A5;
}

.confidence-badge.safe {
    background: var(--emerald-light);
    color: var(--emerald);
    border: 1px solid #6EE7B7;
}

.confidence-badge.warn {
    background: var(--amber-light);
    color: var(--amber);
    border: 1px solid #FCD34D;
}

/* 
   STREAMLIT OVERRIDES
 */
[data-testid="stButton"] > button {
    background: var(--text-dark) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
}

[data-testid="stButton"] > button:hover {
    background: #343A40 !important;
    box-shadow: var(--shadow-sm) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stTextInput"] > div > input,
[data-testid="stTextArea"] textarea {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg-white) !important;
    color: var(--text-dark) !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stTextInput"] > div > input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--emerald) !important;
    box-shadow: 0 0 0 3px var(--emerald-light) !important;
}

[data-testid="stSelectbox"] > div > div {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--border) !important;
    background: var(--bg-white) !important;
}

.stProgress > div > div > div > div {
    background: var(--emerald) !important;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    background: var(--bg-white) !important;
}

/* tab overrides */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg-soft) !important;
    border-radius: var(--radius-sm) !important;
    padding: 4px !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--bg-white) !important;
    box-shadow: var(--shadow-sm) !important;
    color: var(--text-dark) !important;
}

/* divider */
hr { border-color: var(--border) !important; margin: 24px 0 !important; }

/* spinner  */
.stSpinner > div { border-top-color: var(--emerald) !important; }

/* alert boxes */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    border: none !important;
}

/* Plotly chart background fix */
.js-plotly-plot .plotly, .js-plotly-plot .plotly .main-svg {
    border-radius: var(--radius-sm) !important;
}

/* scrollbar  */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-soft); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-light); }

/* 
   PAGE-SPECIFIC: VIDEO LAB
 */
.thumbnail-card {
    background: var(--bg-white);
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

.thumbnail-card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
}

.thumbnail-card .thumb-body {
    padding: 14px 16px;
}

.thumbnail-card .thumb-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-dark);
    line-height: 1.35;
    margin-bottom: 6px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.thumbnail-card .thumb-meta {
    font-size: 0.75rem;
    color: var(--text-light);
}

/* misinfo result banner */
.result-banner {
    padding: 18px 22px;
    border-radius: var(--radius-md);
    border-width: 1px;
    border-style: solid;
    margin-bottom: 20px;
}

.result-banner.danger {
    background: var(--crimson-light);
    border-color: #FCA5A5;
}

.result-banner.safe {
    background: var(--emerald-light);
    border-color: #6EE7B7;
}

.result-banner .result-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 4px;
}

.result-banner .result-reasoning {
    font-size: 0.82rem;
    opacity: 0.8;
    font-family: 'DM Mono', monospace;
}

/* 
   ANIMATIONS
 */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}

@keyframes pulse-border {
    0%, 100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.3); }
    50%       { box-shadow: 0 0 0 8px rgba(16,185,129,0); }
}

.fade-in-up {
    animation: fadeInUp 0.5s ease forwards;
}

.fade-in {
    animation: fadeIn 0.6s ease forwards;
}

/* staggered children */
.fade-in-up:nth-child(1) { animation-delay: 0.05s; }
.fade-in-up:nth-child(2) { animation-delay: 0.10s; }
.fade-in-up:nth-child(3) { animation-delay: 0.15s; }
.fade-in-up:nth-child(4) { animation-delay: 0.20s; }


/* 
   TASK 9: MODEL METRICS MEGA CARD
 */
.metrics-mega-card { background:linear-gradient(135deg,#13161e 0%,#0d1119 100%); border:1px solid #1e2330; border-radius:20px; padding:2rem; margin:1.5rem 0; box-shadow:0 8px 32px rgba(0,212,255,0.08); }
.metrics-card-header { display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2330; }
.metrics-icon { font-size:2.5rem; }
.metrics-card-header h2 { margin:0; font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:800; background:linear-gradient(135deg,#00d4ff,#4a8eff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.metrics-card-header p { margin:4px 0 0; font-size:0.82rem; color:#5a6070; font-family:'DM Mono',monospace; }
.metrics-panels { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:1.5rem; }
.metrics-panel { background:#0d0f14; border:1px solid #1e2330; border-radius:12px; padding:1.2rem; }
.panel-label { font-family:'DM Mono',monospace; font-size:0.78rem; color:#00d4ff; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1rem; }
.metrics-grid-6 { display:grid; grid-template-columns:repeat(3,1fr); gap:0.8rem; }
.metric-cell { text-align:center; background:#13161e; border-radius:10px; padding:0.8rem 0.5rem; }
.metric-value { font-family:'DM Mono',monospace; font-size:1.4rem; font-weight:700; margin-bottom:4px; }
.metric-label { font-size:0.68rem; color:#5a6070; font-family:'DM Mono',monospace; text-transform:uppercase; letter-spacing:0.08em; }
.metric-value.green  { color:#00e5a0; }
.metric-value.blue   { color:#4a8eff; }
.metric-value.amber  { color:#ffb347; }
.metric-value.purple { color:#b388ff; }
.metric-value.cyan   { color:#00d4ff; }
.metric-value.dim    { color:#5a6070; }
.config-row { display:flex; flex-wrap:wrap; align-items:center; gap:0.4rem; padding-top:1rem; border-top:1px solid #1e2330; }
.config-label { font-family:'DM Mono',monospace; font-size:0.72rem; color:#5a6070; margin-right:0.3rem; }
.config-tag { background:#1a1d27; border:1px solid #1e2330; border-radius:4px; padding:3px 10px; font-family:'DM Mono',monospace; font-size:0.7rem; color:#8090a0; }

/* 
   TASK 10: DATASET OVERVIEW CARD
 */
.dataset-overview-card { background:linear-gradient(135deg,#13161e,#0d1119); border:1px solid #1e2330; border-radius:20px; padding:2rem; margin:1.5rem 0; }
.dataset-header { display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem; padding-bottom:1rem; border-bottom:1px solid #1e2330; }
.dataset-header h2 { margin:0; font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:800; background:linear-gradient(135deg,#00d4ff,#b388ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.dataset-header p { margin:4px 0 0; font-size:0.82rem; color:#5a6070; font-family:'DM Mono',monospace; }
.dataset-panels { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:1.5rem; }
.dataset-panel { background:#0d0f14; border:1px solid #1e2330; border-radius:12px; padding:1.2rem; }
.dataset-panel-title { font-family:'Syne',sans-serif; font-size:0.95rem; font-weight:700; color:#e8eaf0; margin-bottom:4px; }
.dataset-file { font-family:'DM Mono',monospace; font-size:0.72rem; color:#00d4ff; margin-bottom:1rem; }
.dataset-stats-row { display:grid; grid-template-columns:repeat(4,1fr); gap:0.5rem; margin-bottom:1rem; }
.ds-stat { background:#13161e; border-radius:8px; padding:0.6rem; text-align:center; }
.ds-val { display:block; font-family:'DM Mono',monospace; font-size:1.2rem; font-weight:700; color:#00e5a0; }
.ds-label { display:block; font-size:0.65rem; color:#5a6070; text-transform:uppercase; letter-spacing:0.08em; margin-top:2px; }
.ds-columns-title { font-family:'DM Mono',monospace; font-size:0.68rem; color:#5a6070; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px; }
.ds-tags { font-family:'DM Mono',monospace; font-size:0.72rem; color:#8090a0; line-height:1.8; margin-bottom:0.8rem; }
.ds-insight { background:#0d1119; border-left:3px solid #b388ff; padding:0.7rem 1rem; border-radius:0 8px 8px 0; font-size:0.8rem; color:#c0c4cc; line-height:1.6; }
.ds-benefits { display:grid; grid-template-columns:repeat(3,1fr); gap:0.6rem; padding-top:1rem; border-top:1px solid #1e2330; }
.ds-benefit-item { background:#13161e; border:1px solid #1e2330; border-radius:8px; padding:0.6rem 0.9rem; font-size:0.78rem; color:#a0a8b8; font-family:'IBM Plex Sans',sans-serif; }

/* 
   LANDING PAGE
 */

/* Full-page wrapper — centers content vertically */
.landing-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 48px 24px 32px;
    min-height: 30vh;
}

/* Centered page title  (required by spec) */
.centered-title {
    font-family: 'Playfair Display', serif;
    font-weight: 800;
    font-size: clamp(2.2rem, 4.5vw, 3.4rem);
    color: var(--text-dark);
    line-height: 1.15;
    letter-spacing: -0.03em;
    text-align: center;
    margin: 18px auto 0;
    max-width: 780px;
}

.centered-title .accent {
    background: linear-gradient(135deg, var(--emerald), var(--sky));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Badge row above the title */
.landing-badge-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
    margin-bottom: 10px;
}

.landing-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--emerald-light);
    color: var(--emerald);
    border: 1px solid #6EE7B7;
    border-radius: 100px;
    padding: 5px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.04em;
}

.landing-badge.indigo {
    background: var(--indigo-light);
    color: var(--indigo);
    border-color: #A5B4FC;
}

.landing-badge.amber {
    background: var(--amber-light);
    color: var(--amber);
    border-color: #FCD34D;
}

/* Subtitle paragraph below the title */
.landing-subtitle {
    font-size: 1.05rem;
    color: var(--text-mid);
    line-height: 1.7;
    max-width: 660px;
    margin: 20px auto 0;
    text-align: center;
}

/* Wrapper for the CTA button under each nav card */
.landing-cta [data-testid="stButton"] > button {
    background: var(--btn-color, var(--emerald)) !important;
    color: white !important;
    border-radius: var(--radius-md) !important;
    font-size: 0.9rem !important;
    padding: 10px 22px !important;
    width: 100% !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    transition: filter 0.2s ease, transform 0.2s ease !important;
}

.landing-cta [data-testid="stButton"] > button:hover {
    filter: brightness(1.12) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}

/* 
   LANDING NAVIGATION CARDS  (3 large cards)
 */
.landing-nav-card {
    background: var(--bg-white);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    padding: 28px 26px 22px;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.25s ease, transform 0.25s ease;
    height: 100%;
}

.landing-nav-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-4px);
}

.landing-nav-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--card-accent, var(--emerald));
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.landing-card-icon {
    font-size: 2.6rem;
    margin-bottom: 14px;
    display: block;
}

.landing-card-title {
    font-size: 1.18rem;
    font-weight: 800;
    color: var(--text-dark);
    letter-spacing: -0.02em;
    margin-bottom: 6px;
}

.landing-card-file {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-light);
    letter-spacing: 0.04em;
    margin-bottom: 14px;
    word-break: break-all;
}

.landing-card-desc {
    font-size: 0.86rem;
    color: var(--text-mid);
    line-height: 1.65;
    margin-bottom: 18px;
}

.landing-card-stats {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}

.landing-card-stat {
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 6px 12px;
    text-align: center;
    flex: 1;
    min-width: 60px;
}

.landing-card-stat-num {
    display: block;
    font-family: 'DM Mono', monospace;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-dark);
    line-height: 1.2;
}

.landing-card-stat-lbl {
    display: block;
    font-size: 0.62rem;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    margin-top: 2px;
}

/* 
   SUB-PAGE TOP-LEFT HEADER  (_render_sub_header)
 */
.app-title-left {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0 18px;
}

.app-icon {
    font-size: 1.9rem;
    line-height: 1;
}

.app-name {
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--text-dark);
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.app-tagline {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-light);
    letter-spacing: 0.06em;
    margin-top: 2px;
}

/* Back / Home button wrapper */
.back-btn {
    padding-top: 6px;
}

.back-btn [data-testid="stButton"] > button {
    background: var(--bg-white) !important;
    color: var(--text-mid) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.82rem !important;
    padding: 7px 16px !important;
}

.back-btn [data-testid="stButton"] > button:hover {
    background: var(--bg-soft) !important;
    border-color: var(--text-mid) !important;
    transform: none !important;
}

/* 
   DATASET DETAIL PAGE — SECTION CARDS
 */

/* Section divider banner */
.section-divider {
    background: linear-gradient(90deg, var(--bg-soft), transparent);
    border-left: 3px solid var(--emerald);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 8px 18px;
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text-mid);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-family: 'DM Mono', monospace;
    margin-bottom: 16px;
}

/* Elevated section card */
.section-card {
    background: var(--bg-white);
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    padding: 20px 22px;
    height: 100%;
    transition: box-shadow 0.2s ease;
}

.section-card:hover {
    box-shadow: var(--shadow-md);
}

.section-card-title {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-light);
    font-family: 'DM Mono', monospace;
    margin-bottom: 14px;
    display: block;
}

/* Dataset info key/value rows */
.ds-info-stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid var(--border);
}

.ds-info-stat:last-child {
    border-bottom: none;
}

.ds-info-key {
    font-size: 0.8rem;
    color: var(--text-mid);
    font-weight: 500;
}

.ds-info-val {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text-dark);
    font-family: 'DM Mono', monospace;
}

/* 
   CONFUSION MATRIX GRID
 */
.cm-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 10px;
}

.cm-cell {
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    padding: 14px 10px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.cm-val {
    font-family: 'DM Mono', monospace;
    font-size: 1.7rem;
    font-weight: 800;
    line-height: 1;
    display: block;
}

.cm-lbl {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    display: block;
}

/* 
   TRAINING CONFIGURATION ROWS
 */
.config-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
}

.config-item:last-child {
    border-bottom: none;
}

.config-key {
    font-size: 0.8rem;
    color: var(--text-mid);
    font-weight: 500;
}

.config-val {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text-dark);
    background: var(--bg-soft);
    padding: 2px 8px;
    border-radius: 4px;
}

/* 
   GENERAL INFORMATION OVERVIEW CARD  (footer section)
 */
.general-info-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #F0FDF7 55%, #EEF2FF 100%);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-md);
    padding: 32px 36px;
    margin: 36px 0 24px;
    position: relative;
    overflow: hidden;
}

.general-info-card::after {
    content: '';
    position: absolute;
    bottom: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(99,102,241,0.06), transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.gi-header {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 24px;
    padding-bottom: 18px;
    border-bottom: 1px solid var(--border);
}

.gi-icon {
    font-size: 2.2rem;
    line-height: 1;
    margin-top: 2px;
}

.gi-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--text-dark);
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.gi-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--text-light);
    margin-top: 4px;
    letter-spacing: 0.05em;
}

.general-info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}

@media (max-width: 900px) {
    .general-info-grid {
        grid-template-columns: 1fr 1fr;
    }
}

.gi-block {
    background: var(--bg-white);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 14px 16px;
    box-shadow: var(--shadow-sm);
}

.gi-block-title {
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--text-dark);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'DM Mono', monospace;
    margin-bottom: 8px;
}

.gi-block-body {
    font-size: 0.83rem;
    color: var(--text-mid);
    line-height: 1.62;
}

.gi-insight {
    background: var(--indigo-light);
    border-left: 3px solid var(--indigo);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 12px 18px;
    font-size: 0.85rem;
    color: var(--text-mid);
    line-height: 1.65;
}

</style>
"""


#  Component Templates 

def metric_card_html(icon: str, value: str, label: str,
                     color: str = "#10B981", delta: str = "") -> str:
    delta_html = f'<span class="metric-delta up">{delta}</span>' if delta else ""
    return f"""
<div class="metric-card fade-in-up" style="--bar-color:{color}">
    {delta_html}
    <span class="metric-icon">{icon}</span>
    <div class="metric-value">{value}</div>
    <div class="metric-label">{label}</div>
</div>
"""


def progress_bar_html(name: str, value: float, color: str,
                      icon: str = "", delay: float = 0.0) -> str:
    pct = round(value * 100, 2)
    delay_style = f"animation-delay:{delay}s" if delay else ""
    return f"""
<div class="metric-bar-wrap fade-in-up">
    <div class="metric-bar-header">
        <span class="metric-bar-name">{icon}&nbsp;{name}</span>
        <span class="metric-bar-value">{pct:.1f}%</span>
    </div>
    <div class="bar-track">
        <div class="bar-fill" style="--target-width:{pct}%;
             background:linear-gradient(90deg,{color}99,{color});
             {delay_style}"></div>
    </div>
</div>
"""


def epoch_bars_html(epochs_data: list) -> str:
    rows = ""
    for i, (val, color) in enumerate(epochs_data):
        pct = round(val * 100, 1)
        rows += f"""
    <div class="epoch-bar-row">
        <span class="epoch-label">Ep {i+1:02d}</span>
        <div class="epoch-track">
            <div class="epoch-fill"
                 style="--target-width:{pct}%;
                        width:{pct}%;
                        background:{color};
                        animation-delay:{i*0.08}s"></div>
        </div>
        <span class="epoch-val" style="color:{color}">{pct:.1f}%</span>
    </div>
"""
    return f'<div class="epoch-bar-container">\n{rows}\n</div>'


def stat_grid_html(stats: list) -> str:
    boxes = ""
    for num, desc in stats:
        boxes += f"""
    <div class="stat-box">
        <span class="stat-num">{num}</span>
        <span class="stat-desc">{desc}</span>
    </div>
"""
    return f'<div class="stat-grid">{boxes}</div>'


def hero_section_html(title_main: str, title_accent: str,
                      subtitle: str, badges: list) -> str:
    badge_html = "".join(
        f'<span class="confidence-badge safe" style="font-size:0.78rem">{b}</span>&nbsp;'
        for b in badges
    )
    return f"""
<div class="hero-section fade-in">
    <div class="section-label" style="margin-bottom:14px"></div>
    <div class="display-title">
        {title_main}<br>
        <span class="accent">{title_accent}</span>
    </div>
    <p style="max-width:600px; color:var(--text-mid);
              font-size:1.05rem; margin:18px 0 22px; line-height:1.65;">
        {subtitle}
    </p>
    <div style="display:flex;gap:8px;flex-wrap:wrap">
        {badge_html}
    </div>
</div>
"""


def video_info_grid_html(meta: dict) -> str:
    tags_html = "".join(
        f'<span class="tag-chip">{t}</span>'
        for t in (meta.get("tags") or [])[:14]
    )
    return f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:20px">

    <div class="vcard-mini">
        <div class="section-label" style="margin-bottom:8px">🏷️ Tags</div>
        <div style="margin-top:6px">{tags_html or '<span style="color:var(--text-light);font-size:0.82rem">No tags</span>'}</div>
    </div>

    <div class="vcard-mini">
        <div class="section-label" style="margin-bottom:8px">📅 Published</div>
        <div style="font-size:1.1rem;font-weight:600;margin-top:4px">{meta.get('published_at','—')}</div>
        <div style="font-size:0.82rem;color:var(--text-light);margin-top:4px">
            {meta.get('channel_title','—')}
        </div>
    </div>

    <div class="vcard-mini" style="grid-column:1/-1">
        <div class="section-label" style="margin-bottom:8px">📝 Description</div>
        <div style="font-size:0.84rem;color:var(--text-mid);line-height:1.6;
                    max-height:90px;overflow:hidden;text-overflow:ellipsis">
            {(meta.get('description','') or 'No description available.')[:320]}…
        </div>
    </div>

</div>
"""


def result_banner_html(result: dict) -> str:
    is_misinfo = result.get("score", 0) >= 0.5
    cls = "danger" if is_misinfo else "safe"
    icon = "🚨" if is_misinfo else "✅"
    label = result.get("label", "")
    pct = result.get("confidence_pct", 0)
    reasoning = result.get("reasoning", "")[:200]
    return f"""
<div class="result-banner {cls} fade-in-up">
    <div class="result-title">{icon} {label} — {pct}% confidence</div>
    <div class="result-reasoning">{reasoning}</div>
</div>
"""







def landing_card_html(
    icon: str,
    title: str,
    file_label: str,
    desc: str,
    accent_color: str = "#10B981",
    stats: list = None,
) -> str:
    """
    Renders one of the three large navigation cards on the Landing Page.

    Parameters
    ----------
    icon         : emoji icon shown at top of card
    title        : card heading
    file_label   : small mono-font label beneath the title (csv filename / tag)
    desc         : paragraph description
    accent_color : top-border & stat-num colour
    stats        : list of (value, label) tuples for the mini-stat strip
    """
    stats = stats or []

    # Build stat strip
    stat_items = "".join(
        f'<div class="landing-card-stat">'
        f'<span class="landing-card-stat-num" style="color:{accent_color}">{num}</span>'
        f'<span class="landing-card-stat-lbl">{lbl}</span>'
        f'</div>'
        for num, lbl in stats
    )
    stats_html = (
        f'<div class="landing-card-stats">{stat_items}</div>'
        if stat_items else ""
    )

    return f"""
<div class="landing-nav-card" style="--card-accent:{accent_color}">
    <span class="landing-card-icon">{icon}</span>
    <div class="landing-card-title">{title}</div>
    <div class="landing-card-file">{file_label}</div>
    <div class="landing-card-desc">{desc}</div>
    {stats_html}
</div>
"""
