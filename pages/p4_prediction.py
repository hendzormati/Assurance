import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.helpers import inject_css, section_header, insight_box, metric_card

AGE_VEHICULE_MAP = {
    "< 1 an": 0,
    "1-2 ans": 1,
    "> 2 ans": 2,
}

SEG_COLORS = {
    "certain": "#10B981",
    "uncertain": "#1B4FD8",
    "unlikely": "#94A3B8",
}

SEG_BG = {
    "certain": "#D1FAE5",
    "uncertain": "#DBEAFE",
    "unlikely": "#F1F5F9",
}


@st.cache_resource
def load_model_artifacts():
    try:
        import joblib

        model = joblib.load("model_outputs/best_rf_model.pkl")
        feat_names = joblib.load("model_outputs/feature_names.pkl")

        scalers = {
            "std": joblib.load("model_outputs/standard_scaler.pkl"),
            "mm": joblib.load("model_outputs/minmax_scaler.pkl"),
            "rob": joblib.load("model_outputs/robust_scaler.pkl"),
        }

        return model, feat_names, scalers, True

    except Exception as e:
        st.warning(f"Modèle non chargé : {e}")
        return None, None, None, False


def mock_predict(inputs: dict) -> float:
    score = 0.08

    if inputs["vehicule_endommage"] == "Yes":
        score += 0.35

    if inputs["ancien_assure"] == 0:
        score += 0.25

    age = inputs["age"]

    if 25 <= age <= 45:
        score += 0.08
    elif age > 60:
        score -= 0.04

    if inputs["prime_annuelle"] < 25000:
        score += 0.02

    return float(np.clip(score, 0.01, 0.99))


def segment_label(p, threshold):
    if p >= threshold:
        return "Certain", "certain"
    elif p >= 0.25:
        return "Incertain", "uncertain"
    else:
        return "Improbable", "unlikely"


def _build_feature_row(inputs, feat_names):
    row = pd.DataFrame([{
        "age": inputs["age"],
        "prime_annuelle": inputs["prime_annuelle"],
        "anciennete": inputs["anciennete"],

        "permis_conduire": inputs["permis_conduire"],
        "ancien_assure": inputs["ancien_assure"],

        "vehicule_endommage_oui": 1 if inputs["vehicule_endommage"] == "Yes" else 0,
        "vehicule_endommage_no": 0 if inputs["vehicule_endommage"] == "Yes" else 1,

        "genre_male": 1 if inputs["genre"] == "Male" else 0,
        "genre_femelle": 0 if inputs["genre"] == "Male" else 1,

        "ancien_assure_1": inputs["ancien_assure"],
        "ancien_assure_0": 1 - inputs["ancien_assure"],

        "permis_conduire_1": inputs["permis_conduire"],
        "permis_conduire_0": 1 - inputs["permis_conduire"],

        "age_vehicule": AGE_VEHICULE_MAP.get(inputs["age_vehicule"], 1),

        "tranche_age": (
            0 if inputs["age"] < 25
            else 1 if inputs["age"] < 45
            else 2 if inputs["age"] < 60
            else 3
        ),

        "canal_communication_encoded": inputs["canal_communication_encoded"],
        "code_regional_encoded": inputs["code_regional"],
    }])

    for col in feat_names:
        if col not in row.columns:
            row[col] = 0

    return row[feat_names]


def predict_real_or_mock(inputs, model, feat_names, model_loaded):
    if model_loaded:
        try:
            row = _build_feature_row(inputs, feat_names)
            return float(model.predict_proba(row)[0][1])
        except Exception as e:
            st.warning(f"Erreur pendant la prédiction réelle : {e}")
            return mock_predict(inputs)

    return mock_predict(inputs)


def _explain_factors(inputs):
    factors = []

    if inputs.get("vehicule_endommage") == "Yes":
        factors.append(("🚗", "Véhicule déjà endommagé : signal important dans le modèle."))

    if inputs.get("vehicule_endommage") == "No":
        factors.append(("🚙", "Véhicule non endommagé : profil généralement moins réceptif."))

    if inputs.get("ancien_assure") == 0:
        factors.append(("🆕", "Client non assuré auparavant : profil potentiellement intéressant."))

    if inputs.get("ancien_assure") == 1:
        factors.append(("🛡️", "Client déjà assuré : comportement différent selon l’historique."))

    if 25 <= inputs.get("age", 35) <= 45:
        factors.append(("👤", "Âge situé dans une tranche active du portefeuille."))

    if inputs.get("prime_annuelle", 30000) < 25000:
        factors.append(("💶", "Prime annuelle faible : variable à interpréter avec prudence car son importance finale est faible."))

    if not factors:
        factors.append(("ℹ️", "Profil neutre."))

    return factors[:4]


def _get_typical_profiles():
    return [
        {
            "name": "Prospect idéal",
            "inputs": dict(
                age=32,
                vehicule_endommage="Yes",
                ancien_assure=0,
                prime_annuelle=22000,
                anciennete=60,
                genre="Male",
                permis_conduire=1,
                age_vehicule="1-2 ans",
                canal_communication_encoded=124,
                canal_label="124",
                code_regional=28,
            ),
        },
        {
            "name": "Client fidèle",
            "inputs": dict(
                age=48,
                vehicule_endommage="No",
                ancien_assure=1,
                prime_annuelle=35000,
                anciennete=200,
                genre="Female",
                permis_conduire=1,
                age_vehicule="> 2 ans",
                canal_communication_encoded=152,
                canal_label="152",
                code_regional=15,
            ),
        },
        {
            "name": "Jeune conducteur",
            "inputs": dict(
                age=22,
                vehicule_endommage="Yes",
                ancien_assure=0,
                prime_annuelle=15000,
                anciennete=30,
                genre="Male",
                permis_conduire=1,
                age_vehicule="< 1 an",
                canal_communication_encoded=160,
                canal_label="160",
                code_regional=10,
            ),
        },
        {
            "name": "Senior prudent",
            "inputs": dict(
                age=67,
                vehicule_endommage="No",
                ancien_assure=1,
                prime_annuelle=45000,
                anciennete=250,
                genre="Female",
                permis_conduire=1,
                age_vehicule="> 2 ans",
                canal_communication_encoded=124,
                canal_label="124",
                code_regional=33,
            ),
        },
    ]


def show():
    inject_css()

    model, feat_names, scalers, model_loaded = load_model_artifacts()

    st.markdown('<div class="page-title">Prédiction individuelle</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Simulez la probabilité de souscription pour un nouveau client</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if not model_loaded:
        st.info("Modèle non chargé — mode démo actif.")

    section_header("Profil client")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("**Informations personnelles**")

        age = st.slider("Âge", 18, 85, 35)

        genre = st.selectbox(
            "Genre",
            ["Male", "Female"],
            format_func=lambda x: "Homme" if x == "Male" else "Femme",
        )

        permis = st.selectbox(
            "Permis de conduire",
            [1, 0],
            format_func=lambda x: "Oui" if x == 1 else "Non",
        )

    with col_b:
        st.markdown("**Véhicule & historique**")

        ancien_assure = st.selectbox(
            "Déjà assuré auparavant ?",
            [0, 1],
            format_func=lambda x: "Non" if x == 0 else "Oui",
        )

        vehicule_endommage = st.selectbox(
            "Véhicule déjà endommagé ?",
            ["Yes", "No"],
            format_func=lambda x: "Oui" if x == "Yes" else "Non",
        )

        age_vehicule = st.selectbox(
            "Âge du véhicule",
            list(AGE_VEHICULE_MAP.keys()),
        )

    with col_c:
        st.markdown("**Contrat actuel**")

        prime_annuelle = st.number_input(
            "Prime annuelle (€)",
            min_value=2000,
            max_value=100000,
            value=28000,
            step=500,
        )

        anciennete = st.slider(
            "Ancienneté client (jours)",
            10,
            300,
            120,
        )

        canal = st.number_input(
            "Canal de communication (code)",
            min_value=0,
            max_value=999,
            value=124,
            step=1,
        )

        code_regional = st.number_input(
            "Code régional",
            min_value=1,
            max_value=54,
            value=28,
        )

    threshold = st.slider(
        "Seuil de décision",
        0.20,
        0.65,
        0.40,
        0.01,
        help="Seuil utilisé pour classer le client comme intéressant à contacter.",
    )

    predict_btn = st.button(
        "Calculer la probabilité",
        type="primary",
        use_container_width=True,
    )

    inputs = dict(
        age=age,
        genre=genre,
        permis_conduire=permis,
        ancien_assure=ancien_assure,
        vehicule_endommage=vehicule_endommage,
        age_vehicule=age_vehicule,
        prime_annuelle=prime_annuelle,
        anciennete=anciennete,
        canal_communication_encoded=int(canal),
        canal_label=str(canal),
        code_regional=code_regional,
    )

    if predict_btn:
        proba = predict_real_or_mock(inputs, model, feat_names, model_loaded)
        st.session_state["last_proba"] = proba
        st.session_state["last_inputs"] = inputs

    if "last_proba" in st.session_state:
        proba = st.session_state["last_proba"]
        inputs = st.session_state["last_inputs"]

        label, seg = segment_label(proba, threshold)
        color = SEG_COLORS[seg]

        section_header("Résultat de la prédiction")

        col_gauge, col_verdict = st.columns([1, 1.2])

        with col_gauge:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round(proba * 100, 1),
                number={
                    "suffix": "%",
                    "font": {
                        "size": 38,
                        "color": color,
                    },
                },
                gauge=dict(
                    axis=dict(
                        range=[0, 100],
                        tickwidth=1,
                        tickcolor="#e2e8f0",
                    ),
                    bar=dict(
                        color=color,
                        thickness=0.28,
                    ),
                    bgcolor="white",
                    borderwidth=0,
                    steps=[
                        dict(range=[0, 25], color="#F1F5F9"),
                        dict(range=[25, threshold * 100], color="#EFF6FF"),
                        dict(range=[threshold * 100, 100], color="#DBEAFE"),
                    ],
                    threshold=dict(
                        line=dict(color="#0A0F1E", width=2),
                        thickness=0.75,
                        value=threshold * 100,
                    ),
                ),
                title={
                    "text": "Probabilité de souscription",
                    "font": {
                        "size": 13,
                        "color": "#64748b",
                    },
                },
            ))

            fig_gauge.update_layout(
                height=260,
                margin=dict(t=30, b=10, l=20, r=20),
                paper_bgcolor="white",
            )

            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_verdict:
            recommendation = "Contacter" if seg != "unlikely" else "Passer"

            st.markdown(f"""
            <div style="background:{SEG_BG[seg]};border-radius:12px;padding:1.4rem 1.6rem;
                        border:2px solid {color};margin-top:0.4rem;">
                <div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;
                            color:{color};font-weight:600;margin-bottom:0.4rem;">Verdict</div>
                <div style="font-size:1.9rem;font-weight:700;color:{color};margin-bottom:0.7rem;">
                    {label}
                </div>
                <table style="font-size:0.88rem;border-collapse:collapse;width:100%">
                    <tr>
                        <td style="color:#64748b;padding:2px 0">Probabilité</td>
                        <td style="font-weight:600;color:{color}">{proba * 100:.1f}%</td>
                    </tr>
                    <tr>
                        <td style="color:#64748b;padding:2px 0">Seuil appliqué</td>
                        <td style="font-weight:600">{threshold * 100:.0f}%</td>
                    </tr>
                    <tr>
                        <td style="color:#64748b;padding:2px 0">Canal</td>
                        <td style="font-weight:600">{inputs["canal_label"]}</td>
                    </tr>
                    <tr>
                        <td style="color:#64748b;padding:2px 0">Recommandation</td>
                        <td style="font-weight:600">{recommendation}</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            factors = _explain_factors(inputs)

            st.markdown("**Facteurs clés détectés :**")

            for icon, txt in factors:
                st.markdown(
                    f"<div style='font-size:0.87rem;margin-bottom:3px'>{icon} {txt}</div>",
                    unsafe_allow_html=True,
                )

    section_header("Simulation sur profils-type")

    profiles = _get_typical_profiles()
    cols = st.columns(len(profiles))

    for col, prof in zip(cols, profiles):
        p = predict_real_or_mock(prof["inputs"], model, feat_names, model_loaded)
        lbl, _ = segment_label(p, 0.40)
        col.markdown(
            metric_card(prof["name"], f"{p * 100:.0f}%", lbl),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    section_header("Sensibilité - âge et prime annuelle")

    base = dict(
        age=35,
        genre="Male",
        permis_conduire=1,
        ancien_assure=0,
        vehicule_endommage="Yes",
        age_vehicule="1-2 ans",
        prime_annuelle=28000,
        anciennete=100,
        canal_communication_encoded=124,
        canal_label="124",
        code_regional=28,
    )

    ages = list(range(18, 80, 3))
    primes = [10000, 20000, 30000, 40000, 50000, 60000, 70000]

    age_probas = [
        predict_real_or_mock({**base, "age": a}, model, feat_names, model_loaded)
        for a in ages
    ]

    prime_probas = [
        predict_real_or_mock({**base, "prime_annuelle": p}, model, feat_names, model_loaded)
        for p in primes
    ]

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        fig_age = go.Figure()

        fig_age.add_trace(go.Scatter(
            x=ages,
            y=[p * 100 for p in age_probas],
            mode="lines+markers",
            line=dict(color="#1B4FD8", width=2.5),
            marker=dict(size=6),
        ))

        fig_age.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=280,
            margin=dict(t=30, b=10, l=0, r=0),
            title=dict(
                text="Probabilité selon l'âge",
                font_size=13,
            ),
            xaxis=dict(
                title="Âge",
                showgrid=False,
            ),
            yaxis=dict(
                title="%",
                gridcolor="#F1F5F9",
            ),
        )

        st.plotly_chart(fig_age, use_container_width=True)

    with col_s2:
        fig_prime = go.Figure(go.Bar(
            x=[f"{p // 1000}k€" for p in primes],
            y=[p * 100 for p in prime_probas],
            marker=dict(
                color=[p * 100 for p in prime_probas],
                colorscale=[[0, "#BFDBFE"], [1, "#1B4FD8"]],
                showscale=False,
            ),
            text=[f"{p * 100:.1f}%" for p in prime_probas],
            textposition="outside",
        ))

        fig_prime.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=280,
            margin=dict(t=30, b=10, l=0, r=0),
            title=dict(
                text="Probabilité selon la prime annuelle",
                font_size=13,
            ),
            xaxis=dict(showgrid=False),
            yaxis=dict(
                title="%",
                gridcolor="#F1F5F9",
            ),
        )

        st.plotly_chart(fig_prime, use_container_width=True)

    insight_box(
        "Les résultats doivent être interprétés à partir du modèle final chargé. "
        "Les variables les plus influentes sont principalement liées à "
        "<b>l’état du véhicule</b> et à <b>l’historique d’assurance</b>. "
        "La <b>prime annuelle</b> doit être interprétée avec prudence, car son importance "
        "est faible dans le modèle final."
    )