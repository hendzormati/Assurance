import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.helpers import inject_css, section_header, insight_box, metric_card, COLORS

# ── Load / generate segmented client data ─────────────────────────────────────
@st.cache_data
def load_clients():
    try:
        df = pd.read_csv("model_outputs/predictions_clients_a_contacter.csv")
        if "proba" not in df.columns and "probability" in df.columns:
            df = df.rename(columns={"probability": "proba"})
        return df, True
    except Exception:
        pass
    try:
        df = pd.read_csv("model_outputs/clients_to_contact.csv")
        return df, True
    except Exception:
        pass

    # Synthetic fallback
    np.random.seed(99)
    n = 2000
    proba = np.concatenate([
        np.random.beta(8, 2, int(n * 0.18)),   # certain
        np.random.beta(3, 3, int(n * 0.25)),   # uncertain
        np.random.beta(1, 6, int(n * 0.57)),   # unlikely
    ])
    np.random.shuffle(proba)
    proba = np.clip(proba, 0.01, 0.99)

    df = pd.DataFrame({
        "id_client":           np.arange(1, n + 1),
        "proba":               proba,
        "age":                 np.random.randint(18, 75, n),
        "genre":               np.random.choice(["Male", "Female"], n, p=[0.54, 0.46]),
        "ancien_assure":       np.random.choice([0, 1], n, p=[0.46, 0.54]),
        "vehicule_endommage":  np.random.choice(["Yes", "No"], n, p=[0.50, 0.50]),
        "age_vehicule":        np.random.choice(["< 1 an", "1-2 an", "> 2 ans"], n, p=[0.43, 0.22, 0.35]),
        "prime_annuelle":      np.random.exponential(25000, n) + 8000,
        "anciennete":          np.random.randint(10, 300, n),
        "canal_communication": np.random.choice(["Agent", "Direct", "Internet"], n, p=[0.3, 0.4, 0.3]),
    })
    return df, False


def assign_segment(p, t_high=0.40, t_low=0.25):
    if p >= t_high:   return "Certain"
    elif p >= t_low:  return "Incertain"
    else:             return "Improbable"


SEG_COLORS = {
    "Certain":    "#10B981",
    "Incertain": "#1B4FD8",
    "Improbable": "#94A3B8",
}
SEG_BG = {
    "Certain":    "#D1FAE5",
    "Incertain": "#DBEAFE",
    "Improbable": "#F1F5F9",
}


def show():
    inject_css()

    df_raw, real = load_clients()

    st.markdown('<div class="page-title">Aide à la décision</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Segmentation des clients et profilage des zones cibles</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if not real:
        st.info("Données synthétiques - placez `predictions_clients_a_contacter.csv` dans `model_outputs/` pour utiliser vos vraies prédictions.")

    # ── Threshold sliders ──────────────────────────────────────────────────────
    col_sl1, col_sl2, _ = st.columns([1, 1, 1])
    with col_sl1:
        t_high = st.slider("Seuil zone CERTAINE", 0.30, 0.70, 0.40, 0.01)
    with col_sl2:
        t_low  = st.slider("Seuil zone INCERTAINE", 0.10, 0.40, 0.25, 0.01)

    df = df_raw.copy()
    df["segment"] = df["proba"].apply(lambda p: assign_segment(p, t_high, t_low))

    certain   = df[df["segment"] == "Certain"]
    uncertain = df[df["segment"] == "Incertain"]
    unlikely  = df[df["segment"] == "Improbable"]

    # ── KPI bar ────────────────────────────────────────────────────────────────
    section_header("Vue d'ensemble - segmentation")

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Total clients", f"{len(df):,}", "base de prédiction"), unsafe_allow_html=True)
    c2.markdown(metric_card("Certains",    f"{len(certain):,}",   f"{len(certain)/len(df)*100:.1f}% du total"), unsafe_allow_html=True)
    c3.markdown(metric_card("Incertains", f"{len(uncertain):,}", f"{len(uncertain)/len(df)*100:.1f}% du total"), unsafe_allow_html=True)
    c4.markdown(metric_card("Improbables", f"{len(unlikely):,}",  f"{len(unlikely)/len(df)*100:.1f}% du total"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3-zone proba distribution ──────────────────────────────────────────────
    col_dist, col_pie = st.columns([1.6, 1])

    with col_dist:
        fig_dist = go.Figure()
        for seg, color in SEG_COLORS.items():
            sub = df[df["segment"] == seg]
            fig_dist.add_trace(go.Histogram(
                x=sub["proba"] * 100,
                name=seg,
                marker_color=color,
                opacity=0.80,
                nbinsx=40,
                hovertemplate=seg + "<br>Proba: %{x:.1f}%<br>Clients: %{y}<extra></extra>",
            ))
        fig_dist.add_vline(x=t_high * 100, line_dash="dot", line_color="#0A0F1E", line_width=1.5,
                           annotation_text=f"Seuil haut {t_high*100:.0f}%", annotation_position="top right",
                           annotation_font_size=10)
        fig_dist.add_vline(x=t_low * 100, line_dash="dash", line_color="#94A3B8", line_width=1,
                           annotation_text=f"Seuil bas {t_low*100:.0f}%", annotation_position="top left",
                           annotation_font_size=10)
        fig_dist.update_layout(
            barmode="stack",
            plot_bgcolor="white", paper_bgcolor="white",
            height=320, margin=dict(t=20, b=10, l=0, r=0),
            xaxis=dict(title="Probabilité de souscription (%)", showgrid=False),
            yaxis=dict(title="Nombre de clients", gridcolor="#F1F5F9"),
            legend=dict(orientation="h", y=1.08),
            title=dict(text="Distribution des probabilités par segment", font_size=13),
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_pie:
        counts = df["segment"].value_counts().reset_index()
        counts.columns = ["segment", "count"]
        fig_pie = px.pie(counts, names="segment", values="count",
                         hole=0.55,
                         color="segment",
                         color_discrete_map=SEG_COLORS,
                         height=320)
        fig_pie.update_layout(margin=dict(t=20, b=0, l=0, r=0),
                              legend=dict(font_size=10, orientation="v"),
                              title=dict(text="Répartition des segments", font_size=13))
        fig_pie.update_traces(textinfo="percent+label",
                              hovertemplate="%{label}<br>%{value:,} clients<extra></extra>")
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Profil des zones ───────────────────────────────────────────────────────
    section_header("Profilage des segments - variables clés")

    seg_choice = st.radio("Segment à analyser", ["Certain", "Incertain", "Comparaison globale"],
                          horizontal=True)

    if seg_choice == "Comparaison globale":
        _show_comparison(df)
    else:
        _show_segment_profile(df, seg_choice)

    # ── Top clients à contacter ────────────────────────────────────────────────
    section_header("Top clients à contacter")

    tab_certain, tab_uncertain = st.tabs(["Certains (priorité haute)", "Incertains (à convaincre)"])

    with tab_certain:
        top_c = certain.sort_values("proba", ascending=False).head(20)
        _show_client_table(top_c)

    with tab_uncertain:
        top_u = uncertain.sort_values("proba", ascending=False).head(20)
        _show_client_table(top_u)

    # ── Canal recommandé ──────────────────────────────────────────────────────
    if "canal_communication" in df.columns:
        section_header("Stratégie de contact par canal")
        _show_canal_strategy(certain, uncertain)

    # ── ROI estimator ─────────────────────────────────────────────────────────
    section_header("Estimateur d'impact marketing")
    _show_roi(certain, uncertain)


# ── Sub-chart helpers ─────────────────────────────────────────────────────────

def _show_comparison(df):
    cat_vars = [c for c in ["vehicule_endommage", "ancien_assure", "age_vehicule", "genre"] if c in df.columns]
    if not cat_vars:
        return
    sel = st.selectbox("Variable catégorielle", cat_vars, key="cmp_sel")
    rate = df.groupby([sel, "segment"]).size().reset_index(name="count")
    fig = px.bar(rate, x=sel, y="count", color="segment",
                 barmode="group",
                 color_discrete_map=SEG_COLORS,
                 labels={"count": "Clients", "segment": "Segment"},
                 height=340)
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                      margin=dict(t=10, b=10, l=0, r=0),
                      xaxis=dict(showgrid=False),
                      yaxis=dict(gridcolor="#F1F5F9"),
                      legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True)


def _show_segment_profile(df, seg):
    sub = df[df["segment"] == seg]
    color = SEG_COLORS[seg]

    col1, col2 = st.columns(2)

    with col1:
        # Age distribution
        fig_age = px.histogram(sub, x="age", nbins=25, color_discrete_sequence=[color],
                               height=260, labels={"age": "Âge"})
        fig_age.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                              margin=dict(t=30, b=10, l=0, r=0),
                              title=dict(text="Distribution d'âge", font_size=13),
                              xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#F1F5F9"))
        st.plotly_chart(fig_age, use_container_width=True)

    with col2:
        if "vehicule_endommage" in sub.columns:
            vc = sub["vehicule_endommage"].value_counts().reset_index()
            vc.columns = ["Véhicule endommagé", "count"]
            fig_veh = px.pie(vc, names="Véhicule endommagé", values="count", hole=0.5,
                             color_discrete_sequence=[color, "#E2E8F0"], height=260)
            fig_veh.update_layout(margin=dict(t=30, b=0, l=0, r=0),
                                   title=dict(text="Véhicule endommagé", font_size=13))
            st.plotly_chart(fig_veh, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        if "prime_annuelle" in sub.columns:
            fig_prime = px.box(sub, y="prime_annuelle", color_discrete_sequence=[color],
                               height=240, labels={"prime_annuelle": "Prime (€)"})
            fig_prime.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                    margin=dict(t=30, b=10, l=0, r=0),
                                    title=dict(text="Prime annuelle", font_size=13),
                                    yaxis=dict(gridcolor="#F1F5F9"),
                                    xaxis=dict(showgrid=False))
            st.plotly_chart(fig_prime, use_container_width=True)

    with col4:
        if "ancien_assure" in sub.columns:
            vc2 = sub["ancien_assure"].map({0: "Jamais assuré", 1: "Déjà assuré"}).value_counts().reset_index()
            vc2.columns = ["Statut", "count"]
            fig_ass = px.bar(vc2, x="Statut", y="count", color_discrete_sequence=[color],
                             height=240, text="count")
            fig_ass.update_traces(textposition="outside")
            fig_ass.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                   margin=dict(t=30, b=10, l=0, r=0),
                                   title=dict(text="Historique assurance", font_size=13),
                                   xaxis=dict(showgrid=False),
                                   yaxis=dict(gridcolor="#F1F5F9"))
            st.plotly_chart(fig_ass, use_container_width=True)


def _show_client_table(df_sub):
    display_cols = [c for c in ["id_client", "proba", "age", "genre", "vehicule_endommage",
                                 "ancien_assure", "prime_annuelle", "anciennete"] if c in df_sub.columns]
    df_disp = df_sub[display_cols].copy()
    if "proba" in df_disp.columns:
        df_disp["proba"] = (df_disp["proba"] * 100).round(1).astype(str) + "%"
    if "prime_annuelle" in df_disp.columns:
        df_disp["prime_annuelle"] = df_disp["prime_annuelle"].round(0).astype(int).apply(lambda x: f"{x:,} €")
    st.dataframe(df_disp.reset_index(drop=True), use_container_width=True, height=320)


def _show_canal_strategy(certain, uncertain):
    if "canal_communication" not in certain.columns:
        return
    c_canal = certain["canal_communication"].value_counts().rename("Certains")
    u_canal = uncertain["canal_communication"].value_counts().rename("Incertains")
    canal_df = pd.concat([c_canal, u_canal], axis=1).fillna(0).reset_index()
    canal_df.columns = ["Canal", "Certains", "Incertains"]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Certains",    x=canal_df["Canal"], y=canal_df["Certains"],
                         marker_color="#10B981"))
    fig.add_trace(go.Bar(name="Incertains", x=canal_df["Canal"], y=canal_df["Incertains"],
                         marker_color="#1B4FD8"))
    fig.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                      height=280, margin=dict(t=10, b=10, l=0, r=0),
                      xaxis=dict(showgrid=False),
                      yaxis=dict(gridcolor="#F1F5F9", title="Clients"),
                      legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True)
    insight_box("Adaptez le canal de contact au segment : les clients <b>certains</b> peuvent être approchés via n'importe quel canal, tandis que les <b>incertains</b> bénéficieront d'un contact personnalisé par agent.")


def _show_roi(certain, uncertain):
    col_r1, col_r2 = st.columns(2)

    with col_r1:
        conv_rate_c = st.slider("Taux de conversion - Certains (%)", 10, 90, 55, 5)
        conv_rate_u = st.slider("Taux de conversion - Incertains (%)", 1, 40, 15, 1)
        cost_contact = st.number_input("Coût de contact (€/client)", 1, 100, 12)
        revenue_contract = st.number_input("Revenu moyen / contrat signé (€)", 100, 5000, 800)

    with col_r2:
        n_c = len(certain)
        n_u = len(uncertain)
        contracts_c = int(n_c * conv_rate_c / 100)
        contracts_u = int(n_u * conv_rate_u / 100)
        total_contracts = contracts_c + contracts_u
        total_cost    = (n_c + n_u) * cost_contact
        total_revenue = total_contracts * revenue_contract
        roi = (total_revenue - total_cost) / total_cost * 100 if total_cost > 0 else 0

        st.markdown(f"""
        <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:12px;
                    padding:1.2rem 1.4rem;font-size:0.88rem;line-height:2;">
            <b style="font-size:1rem;color:#1B4FD8">📈 Projection ROI</b><br>
            Contrats Certains   : <b>{contracts_c:,}</b><br>
            Contrats Incertains : <b>{contracts_u:,}</b><br>
            <hr style="border:none;border-top:1px solid #BFDBFE;margin:0.4rem 0">
            Contrats totaux estimés : <b>{total_contracts:,}</b><br>
            Coût total de contact   : <b>{total_cost:,} €</b><br>
            Revenu total estimé     : <b style="color:#10B981">{total_revenue:,} €</b><br>
            <b style="font-size:1.1rem;color:#10B981">ROI = {roi:.0f}%</b>
        </div>""", unsafe_allow_html=True)
