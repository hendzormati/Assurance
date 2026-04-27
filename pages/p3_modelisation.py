import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import inject_css, section_header, insight_box, get_model_results, get_threshold_data, get_feature_importance, COLORS

def show():
    inject_css()

    st.markdown('<div class="page-title">Modélisation</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Comparaison des modèles, optimisation des hyperparamètres et interprétabilité</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df_models = get_model_results()

    # ── Model comparison ──────────────────────────────────────────────────────
    section_header("Comparaison des modèles")

    metric_choice = st.radio(
        "Trier par", ["recall","f1","roc_auc","accuracy"],
        horizontal=True,
        format_func=lambda x: {"recall":"Recall","f1":"F1-score","roc_auc":"ROC AUC","accuracy":"Accuracy"}[x],
        key="metric_radio"
    )

    df_sorted = df_models.sort_values(metric_choice, ascending=True)
    highlight = df_sorted["model"] == "RF Randomized ★"
    colors_bar = ["#1B4FD8" if h else "#CBD5E1" for h in highlight]

    fig_compare = go.Figure()
    for col, color, name in [
        ("recall",  "#1B4FD8", "Recall"),
        ("f1",      "#06B6D4", "F1-score"),
        ("roc_auc", "#10B981", "ROC AUC"),
    ]:
        visible = True if col == metric_choice else "legendonly"
        fig_compare.add_trace(go.Bar(
            y=df_sorted["model"],
            x=df_sorted[col] * 100,
            name=name,
            orientation="h",
            marker_color=color,
            opacity=0.85,
            visible=visible,
            hovertemplate="%{y}<br>" + name + ": %{x:.1f}%<extra></extra>",
        ))

    fig_compare.update_layout(
        barmode="group",
        plot_bgcolor="white", paper_bgcolor="white",
        height=400,
        margin=dict(t=10, b=10, l=0, r=10),
        xaxis=dict(title="%", gridcolor="#F1F5F9", range=[0,105]),
        yaxis=dict(showgrid=False),
        legend=dict(orientation="h", y=1.05),
    )
    fig_compare.add_vline(x=df_sorted[metric_choice].max()*100,
                          line_dash="dot", line_color="#64748b", line_width=1)
    st.plotly_chart(fig_compare, use_container_width=True)

    # Scatter: recall vs F1 colored by family
    section_header("Recall vs F1 - arbitrage des modèles")

    def model_family(name):
        if "RF" in name: return "Random Forest"
        if "XGB" in name: return "XGBoost"
        if "GBM" in name: return "Gradient Boosting"
        return "LightGBM"

    df_models["family"] = df_models["model"].apply(model_family)

    fig_scatter = px.scatter(
        df_models, x="recall", y="f1",
        color="family",
        symbol="family",
        text="model",
        size=[10]*len(df_models),
        color_discrete_sequence=["#1B4FD8","#06B6D4","#EF4444","#10B981"],
        labels={"recall":"Recall (classe positive)","f1":"F1-score (classe positive)"},
        height=380,
    )
    fig_scatter.update_traces(textposition="top center", textfont_size=9, marker_size=12)
    fig_scatter.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=10,b=10,l=0,r=0),
        xaxis=dict(gridcolor="#F1F5F9", tickformat=".0%"),
        yaxis=dict(gridcolor="#F1F5F9", tickformat=".0%"),
        legend=dict(title="", orientation="h", y=1.05),
    )
    # highlight best
    best = df_models[df_models["model"]=="RF Randomized ★"]
    fig_scatter.add_trace(go.Scatter(
        x=best["recall"], y=best["f1"],
        mode="markers", marker=dict(size=22, color="rgba(27,79,216,0.2)",
                                    line=dict(color="#1B4FD8", width=2)),
        showlegend=False, hoverinfo="skip",
    ))
    st.plotly_chart(fig_scatter, use_container_width=True)

    insight_box("Le modèle <b>RF Randomized Search</b> (étoile ★) offre le meilleur recall (93.8%) avec un ROC AUC de 85.6%. C'est lui qui minimise les faux négatifs (clients intéressés manqués), ce qui est l'enjeu business principal.")

    # ── Threshold tuning ──────────────────────────────────────────────────────
    section_header("Optimisation du seuil de décision")

    df_thresh = get_threshold_data()

    col_thresh, col_info = st.columns([1.8, 1])
    with col_thresh:
        fig_thresh = go.Figure()
        fig_thresh.add_trace(go.Scatter(
            x=df_thresh["threshold"], y=df_thresh["recall"]*100,
            name="Recall", mode="lines+markers",
            line=dict(color="#1B4FD8", width=2.5),
            marker=dict(size=8),
        ))
        fig_thresh.add_trace(go.Scatter(
            x=df_thresh["threshold"], y=df_thresh["f1"]*100,
            name="F1-score", mode="lines+markers",
            line=dict(color="#10B981", width=2.5, dash="dash"),
            marker=dict(size=8),
        ))
        fig_thresh.add_vrect(x0=0.35, x1=0.45, fillcolor="#1B4FD8", opacity=0.07,
                             annotation_text="Zone recommandée", annotation_position="top left",
                             annotation_font_size=10)
        fig_thresh.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            height=300, margin=dict(t=20,b=10,l=0,r=0),
            xaxis=dict(title="Seuil de décision", gridcolor="#F1F5F9", dtick=0.05),
            yaxis=dict(title="%", gridcolor="#F1F5F9"),
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig_thresh, use_container_width=True)

    with col_info:
        st.markdown("<br>", unsafe_allow_html=True)
        for row in df_thresh.itertuples():
            selected = 0.35 <= row.threshold <= 0.45
            bg = "#EFF6FF" if selected else "#F8F9FF"
            border = "2px solid #1B4FD8" if selected else "1px solid #e2e8f0"
            st.markdown(f"""
            <div style="background:{bg};border:{border};border-radius:8px;
                        padding:0.5rem 0.8rem;margin-bottom:0.4rem;font-size:0.82rem;">
                <b>Seuil {row.threshold:.2f}</b> &nbsp;
                <span style="color:#1B4FD8">R={row.recall*100:.1f}%</span> &nbsp;
                <span style="color:#10B981">F1={row.f1*100:.1f}%</span>
            </div>""", unsafe_allow_html=True)

    # ── Feature importance ────────────────────────────────────────────────────
    section_header("Importance des variables - RF Randomized Search")

    fi = get_feature_importance()

    top_n = st.slider("Nombre de variables à afficher", 5, 15, 10, key="fi_slider")
    fi_top = fi.head(top_n).sort_values("importance")

    fig_fi = go.Figure(go.Bar(
        y=fi_top["feature"],
        x=fi_top["importance"] * 100,
        orientation="h",
        marker=dict(
            color=fi_top["importance"] * 100,
            colorscale=[[0,"#BFDBFE"],[1,"#1B4FD8"]],
            showscale=False,
        ),
        text=(fi_top["importance"]*100).round(1).astype(str) + "%",
        textposition="outside",
        hovertemplate="%{y}<br>Importance: %{x:.2f}%<extra></extra>",
    ))
    fig_fi.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=max(300, top_n * 34),
        margin=dict(t=10, b=10, l=0, r=60),
        xaxis=dict(title="Importance (%)", gridcolor="#F1F5F9", range=[0, fi_top["importance"].max()*115]),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_fi, use_container_width=True)

    # Variable family donut
    col_family, col_txt = st.columns([1, 1])
    with col_family:
        family_map = {
            "prime_annuelle":"Prime & ancienneté", "anciennete":"Prime & ancienneté",
            "age":"Âge client", "tranche_age":"Âge client",
            "vehicule_endommage_oui":"Véhicule","vehicule_endommage_no":"Véhicule",
            "age_vehicule":"Véhicule",
            "ancien_assure_1":"Historique assurance","ancien_assure_0":"Historique assurance",
            "canal_communication_encoded":"Canal & région","code_regional_encoded":"Canal & région",
            "genre_male":"Genre","genre_femelle":"Genre",
            "permis_conduire_1":"Permis","permis_conduire_0":"Permis",
        }
        fi["family"] = fi["feature"].map(family_map).fillna("Autre")
        fi_fam = fi.groupby("family")["importance"].sum().reset_index().sort_values("importance",ascending=False)
        fig_fam = px.pie(fi_fam, names="family", values="importance", hole=0.55,
                         color_discrete_sequence=["#1B4FD8","#06B6D4","#10B981","#F59E0B","#EF4444","#8B5CF6"],
                         height=280)
        fig_fam.update_layout(margin=dict(t=0,b=0,l=0,r=0),
                              legend=dict(font_size=10, orientation="v"),
                              showlegend=True)
        fig_fam.update_traces(textinfo="percent", hovertemplate="%{label}<br>%{percent}<extra></extra>")
        st.plotly_chart(fig_fam, use_container_width=True)

    with col_txt:
        st.markdown("<br><br>", unsafe_allow_html=True)
        insight_box("La <b>prime annuelle</b> et l'<b>ancienneté</b> sont de loin les variables les plus discriminantes, représentant à elles seules ~36% de l'importance totale. L'<b>âge du client</b> et l'<b>historique d'assurance</b> complètent le top 4.")
