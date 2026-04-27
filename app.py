import streamlit as st

st.set_page_config(
    page_title="Assurance Auto",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.helpers import inject_css
inject_css()

# ─────────────────────────────────────────────
# SVG ICONS
# ─────────────────────────────────────────────

ICONS = {
    "car": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M5 17H3a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h1l3-4h8l3 4h1a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-2"/>
        <circle cx="7.5" cy="17.5" r="2.5"/><circle cx="16.5" cy="17.5" r="2.5"/>
    </svg>""",
    "home": """<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
    </svg>""",
    "search": """<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>""",
    "cpu": """<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/>
        <line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/>
        <line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/>
        <line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/>
        <line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>
    </svg>""",
    "target": """<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
    </svg>""",
    "bar-chart": """<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
        <line x1="2" y1="20" x2="22" y2="20"/>
    </svg>""",
}

# ─────────────────────────────────────────────
# SESSION STATE NAVIGATION
# ─────────────────────────────────────────────

if "current_page" not in st.session_state:
    st.session_state.current_page = "Contexte"

NAV_ITEMS = [
    ("Contexte",     "home",      "Contexte"),
    ("Exploration",  "search",    "Exploration"),
    ("Modélisation", "cpu",       "Modélisation"),
    ("Prédiction",   "target",    "Prédiction"),
    ("Décision",     "bar-chart", "Décision"),
]

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
        <div class="logo-circle">{ICONS["car"]}</div>
        <div class="logo-subtitle">Assurance Auto</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)

    for label, icon_key, page_name in NAV_ITEMS:
        active = st.session_state.current_page == page_name

        if active:
            st.markdown(f"""
            <style>
            [data-testid="stSidebar"] div[data-testid="stButton"]:has(button p) button {{
                /* fallback — override below per key */
            }}
            /* Target by button index isn't stable; use nth-child based on order */
            </style>
            """, unsafe_allow_html=True)

        clicked = st.button(
            f"  {label}",
            key=f"nav_{page_name}",
            use_container_width=True,
            type="secondary" if not active else "primary",
        )
        if clicked:
            st.session_state.current_page = page_name
            st.rerun()

    st.markdown("""
    <div class="sidebar-model-card">
        <div class="sidebar-small-title">Modèle final</div>
        <div class="sidebar-model-name">Random Forest Optimisé</div>
        <div class="sidebar-stat green">Recall : 93.8%</div>
        <div class="sidebar-stat cyan">ROC AUC : 85.6%</div>
        <div class="sidebar-stat amber">Seuil : 0.40</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROUTING
# ─────────────────────────────────────────────


page = st.session_state.current_page

if page == "Contexte":
    from pages import p1_contexte
    p1_contexte.show()

elif page == "Exploration":
    from pages import p2_eda
    p2_eda.show()

elif page == "Modélisation":
    from pages import p3_modelisation
    p3_modelisation.show()

elif page == "Prédiction":
    from pages import p4_prediction
    p4_prediction.show()

elif page == "Décision":
    from pages import p5_decision
    p5_decision.show()