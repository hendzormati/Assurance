import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────
# COLORS  (lighter blue palette)
# ─────────────────────────────────────────────────────────────

COLORS = {
    "primary":  "#2563EB",   # lighter royal blue (was #1B4FD8)
    "accent":   "#38BDF8",   # sky blue (was #06B6D4)
    "success":  "#10B981",
    "warning":  "#F59E0B",
    "danger":   "#EF4444",
    "dark":     "#0F172A",
    "mid":      "#64748B",
    "light":    "#F1F5F9",
    "white":    "#FFFFFF",
    "border":   "#E2E8F0",
}


# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
        background: #F8FAFC;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stDecoration"]    { display: none !important; }
    [data-testid="stToolbarActions"]{ display: none !important; }
    [data-testid="stSidebarNav"]    { display: none !important; }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* ───────── Sidebar shell ───────── */

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1628 0%, #0F1E38 55%, #152542 100%) !important;
        border-right: 1px solid #1E3A5F;
        min-width: 265px !important;
        max-width: 265px !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.1rem 0.85rem !important;
    }

    /* ───────── Logo card ───────── */

    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.95rem;
        margin-bottom: 1.2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #2563EB, #38BDF8);
        box-shadow: 0 14px 30px rgba(0,0,0,0.28);
    }

    .logo-circle {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        background: rgba(255,255,255,0.18);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .logo-circle svg { stroke: #ffffff; }

    .logo-subtitle {
        font-size: 1rem;
        font-weight: 700;
        color: white !important;
    }

    /* ───────── Section title ───────── */

    .sidebar-section-title {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #4A7AB5 !important;
        font-weight: 800;
        margin: 0.4rem 0 0.55rem 0.25rem;
    }

    /* ───────── Nav buttons - HTML layer (visible) ───────── */

    .nav-btn {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        width: 100%;
        background: transparent;
        border: 1px solid transparent;
        border-radius: 12px;
        padding: 0.65rem 0.85rem;
        margin-bottom: 0.25rem;
        cursor: pointer;
        transition: all 0.15s ease;
        text-align: left;
        color: #94A3B8;
    }

    .nav-btn:hover {
        background: rgba(37,99,235,0.15);
        border-color: rgba(56,189,248,0.2);
        color: #E2E8F0 !important;
    }

    .nav-btn:hover .nav-icon svg { stroke: #38BDF8; }
    .nav-btn:hover .nav-label    { color: #E2E8F0; }

    .nav-btn.nav-btn-active {
        background: linear-gradient(90deg, rgba(37,99,235,0.9), rgba(56,189,248,0.7));
        border-color: rgba(255,255,255,0.15);
        box-shadow: 0 8px 20px rgba(37,99,235,0.25);
    }

    .nav-btn.nav-btn-active .nav-icon svg { stroke: #ffffff; }
    .nav-btn.nav-btn-active .nav-label    { color: #ffffff; font-weight: 800; }

    .nav-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .nav-icon svg { stroke: #64748B; transition: stroke 0.15s ease; }

    .nav-label {
        font-size: 0.96rem;
        font-weight: 600;
        color: inherit;
        transition: color 0.15s ease;
    }

    /* ───────── Hide the real Streamlit buttons (used only for click events) ───────── */

    .nav-hidden-btn { display: none !important; }


    /* ───────── Model card ───────── */

    .sidebar-model-card {
        margin-top: 1.2rem;
        padding: 1rem;
        border-radius: 17px;
        background: rgba(255,255,255,0.055);
        border: 1px solid rgba(255,255,255,0.09);
        box-shadow: 0 12px 26px rgba(0,0,0,0.22);
    }

    .sidebar-small-title {
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #4A7AB5 !important;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .sidebar-model-name {
        color: #F8FAFC !important;
        font-size: 0.96rem;
        font-weight: 800;
        margin-bottom: 0.65rem;
    }

    .sidebar-stat { font-size: 0.88rem; margin-top: 0.28rem; font-weight: 700; }
    .sidebar-stat.green { color: #10B981 !important; }
    .sidebar-stat.cyan  { color: #38BDF8 !important; }
    .sidebar-stat.amber { color: #F59E0B !important; }

    /* ───────── Main content ───────── */

    .page-title {
        font-size: 2rem;
        font-weight: 800;
        color: #0A0F1E;
        letter-spacing: -0.03em;
        line-height: 1.15;
    }

    .page-subtitle {
        font-size: 1.05rem;
        color: #64748B;
        margin-top: 0.35rem;
        font-weight: 400;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2.2rem 0 1.1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #E2E8F0;
    }

    .section-header .dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563EB, #38BDF8);
        flex-shrink: 0;
    }

    .section-header h3 {
        font-size: 1.16rem;
        font-weight: 800;
        color: #0A0F1E;
        margin: 0;
    }

    .metric-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.25rem 1.35rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 24px rgba(15,23,42,0.045);
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #2563EB, #38BDF8);
    }

    .metric-card .label {
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #64748B;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }

    .metric-card .value {
        font-size: 2rem;
        font-weight: 800;
        color: #0A0F1E;
        line-height: 1.1;
    }

    .metric-card .delta { font-size: 0.88rem; color: #64748B; margin-top: 0.35rem; }
    .metric-card .delta.good { color: #10B981; }
    .metric-card .delta.bad  { color: #EF4444; }

    .insight-box {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-left: 5px solid #2563EB;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin: 0.8rem 0;
        font-size: 0.98rem;
        color: #1E40AF;
        line-height: 1.62;
    }

    .warning-box {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 5px solid #F59E0B;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin: 0.8rem 0;
        color: #92400E;
        line-height: 1.62;
    }

    .badge {
        display: inline-block;
        padding: 0.24rem 0.72rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    .badge-blue  { background: #DBEAFE; color: #1D4ED8; }
    .badge-green { background: #D1FAE5; color: #065F46; }
    .badge-gray  { background: #F1F5F9; color: #475569; }
    .badge-amber { background: #FEF3C7; color: #92400E; }
    .badge-red   { background: #FEE2E2; color: #991B1B; }

    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.96rem;
        background: white;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 10px 24px rgba(15,23,42,0.045);
    }

    .styled-table th {
        background: #F8FAFC;
        color: #64748B;
        font-size: 0.78rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.75rem 0.9rem;
        border-bottom: 1px solid #E2E8F0;
        text-align: left;
    }

    .styled-table td {
        padding: 0.68rem 0.9rem;
        border-bottom: 1px solid #F1F5F9;
        color: #0A0F1E;
    }

    .styled-table tr:hover td { background: #F8FAFC; }

    .step-item {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1rem;
        box-shadow: 0 8px 20px rgba(15,23,42,0.04);
    }

    .step-num {
        width: 34px; height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563EB, #38BDF8);
        color: white;
        font-size: 0.88rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .step-body h4 { margin: 0 0 0.25rem; font-size: 1rem; font-weight: 800; color: #0A0F1E; }
    .step-body p  { margin: 0; font-size: 0.94rem; color: #64748B; line-height: 1.55; }

    .seg-uncertain { background: #DBEAFE; color: #1D4ED8; padding: 4px 12px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; }
    .seg-certain   { background: #D1FAE5; color: #065F46; padding: 4px 12px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; }
    .seg-unlikely  { background: #F1F5F9; color: #475569; padding: 4px 12px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; }

    div[data-testid="stWidgetLabel"] p  { font-size: 0.97rem !important; font-weight: 700 !important; color: #0A0F1E !important; }
    div[data-baseweb="select"] div,
    div[data-baseweb="input"] input     { font-size: 0.96rem !important; }
    div[data-testid="stTabs"] button p  { font-size: 0.96rem !important; font-weight: 700 !important; }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 0.9rem;
        box-shadow: 0 8px 20px rgba(15,23,42,0.035);
    }

    div[data-testid="stMetric"] label {
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B !important;
        font-weight: 800;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 800;
        color: #0A0F1E !important;
    }

    div[data-testid="stDataFrame"] th,
    div[data-testid="stDataFrame"] td { font-size: 0.94rem !important; }

    div[data-testid="stAlert"] p { font-size: 0.96rem !important; }

   /* ── Sidebar nav buttons ── */
[data-testid="stSidebar"] .stButton > div > button {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    padding: 0.65rem 0.85rem !important;
    margin-bottom: 0.25rem !important;
    color: #94A3B8 !important;
    font-size: 0.96rem !important;
    font-weight: 600 !important;
    text-align: left !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > div > button:hover {
    background: rgba(37,99,235,0.15) !important;
    border-color: rgba(56,189,248,0.2) !important;
    color: #E2E8F0 !important;
}             
        /* ── Show sidebar buttons, style them as nav items ── */
[data-testid="stSidebar"] .stButton {
    display: block !important;
}

[data-testid="stSidebar"] .stButton > div > button {
    display: flex !important;
    align-items: center !important;
    width: 100% !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;
    padding: 0.65rem 0.85rem !important;
    margin-bottom: 0.25rem !important;
    color: #94A3B8 !important;
    font-size: 0.96rem !important;
    font-weight: 600 !important;
    text-align: left !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
}

[data-testid="stSidebar"] .stButton > div > button:hover {
    background: rgba(37,99,235,0.15) !important;
    border-color: rgba(56,189,248,0.2) !important;
    color: #E2E8F0 !important;
}
                /* Active nav item */
[data-testid="stSidebar"] .stButton > div > button[kind="primary"] {
    background: linear-gradient(90deg, rgba(37,99,235,0.9), rgba(56,189,248,0.7)) !important;
    border-color: rgba(255,255,255,0.15) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 20px rgba(37,99,235,0.25) !important;
}        
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# UI HELPERS  (unchanged)
# ─────────────────────────────────────────────────────────────

def metric_card(label, value, delta=None, delta_good=True):
    delta_class = "good" if delta_good else "bad"
    delta_html = f'<div class="delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        {delta_html}
    </div>
    """

def section_header(title):
    st.markdown(f"""
    <div class="section-header">
        <div class="dot"></div>
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)

def insight_box(text):
    st.markdown(f'<div class="insight-box"> {text}</div>', unsafe_allow_html=True)

def warning_box(text):
    st.markdown(f'<div class="warning-box"> {text}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MODEL DATA  (unchanged)
# ─────────────────────────────────────────────────────────────

@st.cache_data
def get_model_results():
    return pd.DataFrame({
        "model": ["RF baseline","RF Grid","RF Randomized ★","XGB baseline","XGB Grid","XGB Randomized","GBM baseline","GBM Grid","LightGBM baseline","LightGBM Grid","LightGBM Rand."],
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
        "threshold": [0.30,0.35,0.40,0.45,0.50],
        "recall":    [0.988,0.979,0.978,0.964,0.936],
        "f1":        [0.389,0.405,0.406,0.415,0.427],
    })

@st.cache_data
def get_feature_importance():
    features = ["prime_annuelle","anciennete","age","vehicule_endommage_oui","ancien_assure_1","age_vehicule","canal_communication_encoded","code_regional_encoded","tranche_age","genre_male","permis_conduire_1","ancien_assure_0","vehicule_endommage_no","genre_femelle","permis_conduire_0"]
    importance = [0.198,0.167,0.143,0.108,0.092,0.071,0.058,0.042,0.038,0.025,0.018,0.014,0.011,0.008,0.007]
    return pd.DataFrame({"feature": features, "importance": importance})