import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import inject_css, section_header, insight_box, COLORS

@st.cache_data
def load_train_data():
    """Load real train_info.csv — adjust path as needed."""
    try:
        df = pd.read_csv("data/train_info.csv")
        return df
    except Exception:
        # Synthetic fallback so dashboard runs standalone
        np.random.seed(42)
        n = 5000
        df = pd.DataFrame({
            "age":                np.random.randint(18, 75, n),
            "genre":              np.random.choice(["Male","Female"], n, p=[0.54,0.46]),
            "permis_conduire":    np.random.choice([0,1], n, p=[0.01,0.99]),
            "ancien_assure":      np.random.choice([0,1], n, p=[0.54,0.46]),
            "age_vehicule":       np.random.choice(["< 1 an","1-2 an","> 2 ans"], n, p=[0.43,0.22,0.35]),
            "vehicule_endommage": np.random.choice(["Yes","No"], n, p=[0.50,0.50]),
            "prime_annuelle":     np.random.exponential(30000, n) + 5000,
            "anciennete":         np.random.randint(10, 300, n),
            "reponse_client":     np.random.choice([0,1], n, p=[0.878,0.122]),
        })
        return df


def show():
    inject_css()

    st.markdown('<div class="page-title">Exploration des données</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Analyse descriptive et visualisation des variables clés</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df = load_train_data()

    # ── Dataset overview ──────────────────────────────────────────────────────
    section_header("Vue d'ensemble du dataset")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Observations", f"{len(df):,}")
    c2.metric("Variables", str(df.shape[1]))
    c3.metric("Valeurs manquantes", str(df.isnull().sum().sum()))
    rate = df["reponse_client"].mean() * 100 if "reponse_client" in df.columns else 12.3
    c4.metric("Taux souscription", f"{rate:.1f}%")

    # ── Class balance donut ───────────────────────────────────────────────────
    col_donut, col_desc = st.columns([1, 1.6])

    with col_donut:
        if "reponse_client" in df.columns:
            vc = df["reponse_client"].value_counts()
        else:
            vc = pd.Series({0: 4340, 1: 660})
        fig_donut = go.Figure(go.Pie(
            labels=["Non intéressé (0)", "Intéressé (1)"],
            values=[vc.get(0, 4340), vc.get(1, 660)],
            hole=0.62,
            marker_colors=["#E2E8F0", "#1B4FD8"],
            textinfo="percent",
            hovertemplate="%{label}<br>%{value:,} clients<extra></extra>",
        ))
        fig_donut.update_layout(
            margin=dict(t=20,b=20,l=0,r=0),
            height=240,
            showlegend=True,
            legend=dict(orientation="h", y=-0.1, font_size=11),
            annotations=[dict(text=f"<b>{rate:.0f}%</b><br>positif", x=0.5, y=0.5,
                              font_size=14, showarrow=False)],
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_desc:
        st.markdown("<br>", unsafe_allow_html=True)
        insight_box("Le dataset est fortement déséquilibré : seulement <b>~12%</b> des clients répondent positivement. L'accuracy seule est donc trompeuse — le modèle doit être évalué sur le <b>recall</b> et le <b>ROC AUC</b>.")
        st.markdown("""
        <div style="margin-top:1rem;display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;font-size:0.82rem;">
            <div style="padding:0.5rem 0.8rem;background:#F8F9FF;border-radius:8px;border:1px solid #e2e8f0">
                <span style="color:#64748b">Classe 0</span><br>
                <b style="font-size:1.1rem">87.8%</b> — non intéressé
            </div>
            <div style="padding:0.5rem 0.8rem;background:#EFF6FF;border-radius:8px;border:1px solid #BFDBFE">
                <span style="color:#1D4ED8">Classe 1</span><br>
                <b style="font-size:1.1rem;color:#1D4ED8">12.2%</b> — intéressé
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Interactive variable explorer ─────────────────────────────────────────
    section_header("Exploration interactive des variables")

    cat_cols = [c for c in ["genre","ancien_assure","age_vehicule","vehicule_endommage","permis_conduire"] if c in df.columns]
    num_cols = [c for c in ["age","prime_annuelle","anciennete"] if c in df.columns]

    tab1, tab2 = st.tabs(["📊 Variables catégorielles", "📈 Variables numériques"])

    with tab1:
        if cat_cols:
            sel_cat = st.selectbox("Variable à analyser", cat_cols, key="cat_sel")
            if "reponse_client" in df.columns:
                ct = df.groupby([sel_cat, "reponse_client"]).size().reset_index(name="count")
                ct["label"] = ct["reponse_client"].map({0:"Non intéressé", 1:"Intéressé"})
                fig_cat = px.bar(ct, x=sel_cat, y="count", color="label",
                                 barmode="group",
                                 color_discrete_map={"Non intéressé":"#E2E8F0","Intéressé":"#1B4FD8"},
                                 labels={"count":"Nombre de clients","label":"Réponse"},
                                 height=360)
                fig_cat.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    legend=dict(orientation="h",y=1.05),
                    margin=dict(t=10,b=10,l=0,r=0),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(gridcolor="#F1F5F9"),
                )
                st.plotly_chart(fig_cat, use_container_width=True)

                # Conversion rate per category
                cr = df.groupby(sel_cat)["reponse_client"].mean().reset_index()
                cr.columns = [sel_cat, "taux_souscription"]
                cr["taux_souscription"] = (cr["taux_souscription"] * 100).round(1)
                fig_cr = px.bar(cr, x=sel_cat, y="taux_souscription",
                                color="taux_souscription",
                                color_continuous_scale=["#BFDBFE","#1B4FD8"],
                                labels={"taux_souscription":"Taux (%)"},
                                height=260,
                                text="taux_souscription")
                fig_cr.update_traces(texttemplate="%{text}%", textposition="outside")
                fig_cr.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    coloraxis_showscale=False,
                    margin=dict(t=10,b=10,l=0,r=0),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(gridcolor="#F1F5F9", title="Taux de souscription (%)"),
                    title=dict(text="Taux de souscription par modalité", font_size=13),
                )
                st.plotly_chart(fig_cr, use_container_width=True)

    with tab2:
        if num_cols:
            sel_num = st.selectbox("Variable à analyser", num_cols, key="num_sel")
            col_a, col_b = st.columns(2)

            with col_a:
                if "reponse_client" in df.columns:
                    fig_hist = px.histogram(df, x=sel_num, color=df["reponse_client"].map({0:"Non intéressé",1:"Intéressé"}),
                                            nbins=40, barmode="overlay", opacity=0.75,
                                            color_discrete_map={"Non intéressé":"#CBD5E1","Intéressé":"#1B4FD8"},
                                            labels={sel_num: sel_num, "color":"Réponse"},
                                            height=310)
                else:
                    fig_hist = px.histogram(df, x=sel_num, nbins=40, height=310)
                fig_hist.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(t=30,b=10,l=0,r=0),
                    legend=dict(orientation="h",y=1.05),
                    title=dict(text="Distribution", font_size=13),
                    yaxis=dict(gridcolor="#F1F5F9"),
                    xaxis=dict(showgrid=False),
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            with col_b:
                if "reponse_client" in df.columns:
                    fig_box = px.box(df, x=df["reponse_client"].map({0:"Non intéressé",1:"Intéressé"}),
                                     y=sel_num,
                                     color=df["reponse_client"].map({0:"Non intéressé",1:"Intéressé"}),
                                     color_discrete_map={"Non intéressé":"#CBD5E1","Intéressé":"#1B4FD8"},
                                     height=310)
                    fig_box.update_layout(
                        plot_bgcolor="white", paper_bgcolor="white",
                        margin=dict(t=30,b=10,l=0,r=0),
                        showlegend=False,
                        title=dict(text="Boxplot par réponse", font_size=13),
                        yaxis=dict(gridcolor="#F1F5F9"),
                        xaxis=dict(showgrid=False, title=""),
                    )
                    st.plotly_chart(fig_box, use_container_width=True)

    # ── Descriptive stats table ───────────────────────────────────────────────
    section_header("Statistiques descriptives")
    num_df = df[num_cols] if num_cols else df.select_dtypes(include="number")
    st.dataframe(
        num_df.describe().round(1).T
              .rename(columns={"count":"n","mean":"Moyenne","std":"Écart-type",
                               "min":"Min","25%":"Q1","50%":"Médiane","75%":"Q3","max":"Max"}),
        use_container_width=True,
    )
