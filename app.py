import streamlit as st

st.set_page_config(
    page_title="Assurance Auto · Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.helpers import inject_css
inject_css()

st.markdown("""
<style>
/* ── Kill duplicate auto-generated /pages nav only ── */
[data-testid="stSidebarNav"]           { display: none !important; }

/* ── Sidebar shell ── */
[data-testid="stSidebar"] {
    background: #0A0F1E !important;
    min-width: 255px !important;
    max-width: 255px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ── Radio nav: hide the label above, tighten gap ── */
div[data-testid="stSidebar"] .stRadio > label  { display: none !important; }
div[data-testid="stSidebar"] .stRadio > div    { gap: 2px !important; }

/* ── Each nav item ── */
div[data-testid="stSidebar"] .stRadio > div > label {
    border-radius: 8px;
    padding: 0.8rem 1.2rem !important;
    color: #94a3b8 !important;
    font-size: 1.05rem !important;
    font-weight: 500;
    cursor: pointer;
    width: 100%;
    margin: 0 !important;
    transition: background 0.15s;
}
div[data-testid="stSidebar"] .stRadio > div > label p {
    font-size: 1.05rem !important;
    margin: 0 !important;
    color: inherit !important;
}
div[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: #1e2a45 !important;
    color: #e2e8f0 !important;
}
/* Active (selected) item */
div[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
    background: #1B4FD8 !important;
    color: white !important;
}
div[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 700 !important;
}
/* Hide the radio circle dot */
div[data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

/* ── General sidebar text size ── */
div[data-testid="stSidebar"] p,
div[data-testid="stSidebar"] span,
div[data-testid="stSidebar"] div {
    font-size: 0.95rem;
}

/* ── GLOBAL font size boost ── */
html, body, [class*="css"] {
    font-size: 16px !important;
}

/* Page title / subtitle */
.page-title    { font-size: 1.9rem !important; }
.page-subtitle { font-size: 1.05rem !important; }

/* Section headers */
.section-header h3 { font-size: 1.1rem !important; }

/* Insight box */
.insight-box { font-size: 1rem !important; line-height: 1.6; }

/* Metric card */
.metric-card .label { font-size: 0.82rem !important; }
.metric-card .value { font-size: 2.1rem !important; }
.metric-card .delta { font-size: 0.88rem !important; }

/* Table */
.styled-table      { font-size: 0.97rem !important; }
.styled-table th   { font-size: 0.82rem !important; }

/* Step items */
.step-body h4 { font-size: 1rem !important; }
.step-body p  { font-size: 0.95rem !important; }

/* Badges */
.badge { font-size: 0.82rem !important; }

/* Streamlit native widgets — labels, selects, sliders */
div[data-testid="stWidgetLabel"] p,
div[data-testid="stWidgetLabel"] label,
.stSelectbox label, .stSlider label,
.stRadio label, .stNumberInput label,
.stTextInput label {
    font-size: 1rem !important;
    font-weight: 500 !important;
    color: #0A0F1E !important;
}

/* Selectbox / input text */
div[data-baseweb="select"] div,
div[data-baseweb="input"] input {
    font-size: 0.97rem !important;
}

/* Tab labels */
div[data-testid="stTabs"] button p {
    font-size: 1rem !important;
}

/* Dataframe header / cells */
div[data-testid="stDataFrame"] th,
div[data-testid="stDataFrame"] td {
    font-size: 0.95rem !important;
}

/* st.metric labels & values */
div[data-testid="stMetric"] label  { font-size: 0.9rem !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
}

/* Info / warning boxes */
div[data-testid="stAlert"] p { font-size: 0.97rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.5rem 1.2rem 0.9rem;">
        <div style="font-size:0.75rem;letter-spacing:0.13em;text-transform:uppercase;
                    color:#475569;font-weight:600;margin-bottom:0.45rem;">
            ENSIM · Data Science
        </div>
        <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;line-height:1.3;">
            🚗 Assurance Auto
        </div>
        <div style="font-size:0.88rem;color:#64748b;margin-top:0.25rem;">
            Prédiction de souscription
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #1e2a45;margin:0 0 0.5rem 0;">
    """, unsafe_allow_html=True)

    page_label = st.radio(
        "Navigation",
        [
            "🏠  Contexte",
            "🔍  Exploration",
            "🤖  Modélisation",
            "🎯  Prédiction",
            "📊  Aide à la décision",
        ],
        key="nav_radio",
        label_visibility="collapsed",
    )

    st.markdown("""
    <hr style="border:none;border-top:1px solid #1e2a45;margin:0.8rem 0 0.6rem;">
    <div style="padding:0 1.2rem 1.2rem; line-height:2;">
        <div style="font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;
                    color:#475569;font-weight:600;margin-bottom:0.3rem;">
            Modèle sélectionné
        </div>
        <div style="font-size:0.92rem;color:#94a3b8;">RF Randomized Search</div>
        <span style="color:#10B981;font-size:0.92rem">● Recall 93.8%</span><br>
        <span style="color:#06B6D4;font-size:0.92rem">● ROC AUC 85.6%</span>
    </div>
    """, unsafe_allow_html=True)

# ── Route ─────────────────────────────────────────────────────────────────────
if "Contexte" in page_label:
    from pages import p1_contexte;      p1_contexte.show()
elif "Exploration" in page_label:
    from pages import p2_eda;           p2_eda.show()
elif "Modélisation" in page_label:
    from pages import p3_modelisation;  p3_modelisation.show()
elif "Prédiction" in page_label:
    from pages import p4_prediction;    p4_prediction.show()
elif "Aide" in page_label:
    from pages import p5_decision;      p5_decision.show()