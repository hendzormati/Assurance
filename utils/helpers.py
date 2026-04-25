import pandas as pd
import numpy as np
import streamlit as st

# ── Color palette ─────────────────────────────────────────────────────────────
COLORS = {
    "primary":   "#1B4FD8",
    "accent":    "#06B6D4",
    "success":   "#10B981",
    "warning":   "#F59E0B",
    "danger":    "#EF4444",
    "dark":      "#0A0F1E",
    "mid":       "#64748B",
    "light":     "#F1F5F9",
    "uncertain": "#1B4FD8",
    "certain":   "#10B981",
    "unlikely":  "#94A3B8",
}

SEGMENT_COLORS = {
    "uncertain": "#1B4FD8",
    "certain":   "#10B981",
    "unlikely":  "#94A3B8",
}

# ── Inject global CSS ─────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
    }

    /* Hide footer and hamburger menu only */
    #MainMenu  { visibility: hidden; }
    footer     { visibility: hidden; }

    /* Hide the Deploy button specifically — do NOT touch header or its children */
    [data-testid="stToolbarActions"]          { display: none !important; }
    [data-testid="stToolbarActions"] *        { display: none !important; }
    button[data-testid="stBaseButton-header"] { display: none !important; }
    .stDeployButton                           { display: none !important; }
    [data-testid="stDecoration"]              { display: none !important; }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0A0F1E !important;
        border-right: 1px solid #1e2a45;
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] p {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.05em;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.3rem 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #1B4FD8, #06B6D4);
    }
    .metric-card .label {
        font-size: 0.82rem;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .metric-card .value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0A0F1E;
        line-height: 1.1;
    }
    .metric-card .delta {
        font-size: 0.88rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    .metric-card .delta.good { color: #10B981; }
    .metric-card .delta.bad  { color: #EF4444; }

    /* ── Section headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2.2rem 0 1.1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .section-header .dot {
        width: 9px; height: 9px;
        border-radius: 50%;
        background: #1B4FD8;
        flex-shrink: 0;
    }
    .section-header h3 {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0A0F1E;
        margin: 0;
        letter-spacing: -0.01em;
    }

    /* ── Insight box ── */
    .insight-box {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-left: 4px solid #1B4FD8;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        font-size: 1rem;
        color: #1e40af;
        line-height: 1.6;
    }

    /* ── Badges ── */
    .badge {
        display: inline-block;
        padding: 0.22rem 0.7rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .badge-blue   { background: #DBEAFE; color: #1D4ED8; }
    .badge-green  { background: #D1FAE5; color: #065F46; }
    .badge-gray   { background: #F1F5F9; color: #475569; }
    .badge-amber  { background: #FEF3C7; color: #92400E; }

    /* ── Page title / subtitle ── */
    .page-title {
        font-size: 1.9rem;
        font-weight: 700;
        color: #0A0F1E;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .page-subtitle {
        font-size: 1.05rem;
        color: #64748b;
        margin-top: 0.25rem;
        font-weight: 400;
    }

    /* ── Table ── */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.97rem;
    }
    .styled-table th {
        background: #F8F9FF;
        color: #64748b;
        font-size: 0.82rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 0.7rem 0.9rem;
        border-bottom: 1px solid #e2e8f0;
        text-align: left;
    }
    .styled-table td {
        padding: 0.6rem 0.9rem;
        border-bottom: 1px solid #f1f5f9;
        color: #0A0F1E;
        font-size: 0.97rem;
    }
    .styled-table tr:hover td { background: #F8F9FF; }

    /* ── Segment pills ── */
    .seg-uncertain { background:#DBEAFE; color:#1D4ED8; padding:3px 12px; border-radius:20px; font-size:0.82rem; font-weight:600; }
    .seg-certain   { background:#D1FAE5; color:#065F46; padding:3px 12px; border-radius:20px; font-size:0.82rem; font-weight:600; }
    .seg-unlikely  { background:#F1F5F9; color:#475569; padding:3px 12px; border-radius:20px; font-size:0.82rem; font-weight:600; }

    /* ── Steps timeline ── */
    .step-item { display:flex; gap:1rem; margin-bottom:1.6rem; }
    .step-num  {
        width: 34px; height: 34px;
        border-radius: 50%;
        background: #1B4FD8;
        color: white;
        font-size: 0.88rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .step-body h4 { margin:0 0 0.25rem; font-size:1rem; font-weight:700; color:#0A0F1E; }
    .step-body p  { margin:0; font-size:0.95rem; color:#64748b; line-height:1.55; }

    /* ── Tabs ── */
    div[data-testid="stTabs"] button p {
        font-family: 'DM Sans', sans-serif;
        font-size: 1rem !important;
        font-weight: 500;
    }

    /* ── Widget labels ── */
    div[data-testid="stWidgetLabel"] p {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #0A0F1E !important;
    }

    /* ── Selectbox / input values ── */
    div[data-baseweb="select"] div,
    div[data-baseweb="input"] input {
        font-size: 0.97rem !important;
    }

    /* ── Dataframe ── */
    div[data-testid="stDataFrame"] th,
    div[data-testid="stDataFrame"] td {
        font-size: 0.95rem !important;
    }

    /* ── st.metric ── */
    div[data-testid="stMetric"] label {
        font-size: 0.88rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 700;
    }

    /* ── Alert / info boxes ── */
    div[data-testid="stAlert"] p { font-size: 0.97rem !important; }
    </style>
    """, unsafe_allow_html=True)


def metric_card(label, value, delta=None, delta_good=True):
    delta_class = "good" if delta_good else "bad"
    delta_html  = f'<div class="delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        {delta_html}
    </div>"""


def section_header(title):
    st.markdown(f"""
    <div class="section-header">
        <div class="dot"></div>
        <h3>{title}</h3>
    </div>""", unsafe_allow_html=True)


def insight_box(text):
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)


# ── Mock / sample data generators ─────────────────────────────────────────────
@st.cache_data
def get_model_results():
    return pd.DataFrame({
        "model":    ["RF baseline","RF Grid","RF Randomized ★","XGB baseline",
                     "XGB Grid","XGB Randomized","GBM baseline","GBM Grid",
                     "LightGBM baseline","LightGBM Grid","LightGBM Rand."],
        "accuracy": [0.867,0.698,0.697,0.718,0.711,0.692,0.878,0.872,0.704,0.788,0.731],
        "recall":   [0.117,0.936,0.938,0.905,0.921,0.936,0.000,0.074,0.928,0.719,0.877],
        "f1":       [0.177,0.432,0.431,0.440,0.438,0.427,0.001,0.124,0.435,0.454,0.444],
        "roc_auc":  [0.833,0.856,0.856,0.856,0.858,0.851,0.857,0.849,0.858,0.855,0.853],
        "fp":       [1877,22386,22552,20600,21316,22872,1,1117,21895,13549,19394],
        "fn":       [8254,601,584,889,736,595,9339,8650,671,2628,1150],
    })


@st.cache_data
def get_threshold_data():
    return pd.DataFrame({
        "threshold": [0.30, 0.35, 0.40, 0.45, 0.50],
        "recall":    [0.988, 0.979, 0.978, 0.964, 0.936],
        "f1":        [0.389, 0.405, 0.406, 0.415, 0.427],
    })


@st.cache_data
def get_feature_importance():
    features = [
        "prime_annuelle","anciennete","age","vehicule_endommage_oui",
        "ancien_assure_1","age_vehicule","canal_communication_encoded",
        "code_regional_encoded","tranche_age","genre_male",
        "permis_conduire_1","ancien_assure_0","vehicule_endommage_no",
        "genre_femelle","permis_conduire_0",
    ]
    importance = [0.198,0.167,0.143,0.108,0.092,0.071,0.058,
                  0.042,0.038,0.025,0.018,0.014,0.011,0.008,0.007]
    return pd.DataFrame({"feature": features, "importance": importance})