import streamlit as st
from utils.helpers import inject_css, section_header, insight_box, metric_card

def show():
    inject_css()

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0A0F1E 0%,#1B4FD8 100%);
                border-radius:16px;padding:2.5rem 2rem;margin-bottom:2rem;
                position:relative;overflow:hidden;">
        <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
                    border-radius:50%;background:rgba(6,182,212,0.12);"></div>
        <div style="position:absolute;bottom:-60px;right:80px;width:140px;height:140px;
                    border-radius:50%;background:rgba(255,255,255,0.05);"></div>
        <div style="font-size:0.72rem;letter-spacing:0.12em;text-transform:uppercase;
                    color:#06B6D4;font-weight:600;margin-bottom:0.6rem;">
            ENSIM · Data Science Project
        </div>
        <div style="font-size:2rem;font-weight:700;color:white;letter-spacing:-0.02em;
                    line-height:1.15;margin-bottom:0.6rem;">
            Prédiction de souscription<br>d'assurance automobile
        </div>
        <div style="font-size:0.92rem;color:#94a3b8;max-width:560px;line-height:1.6;">
            Modèle prédictif pour anticiper la probabilité qu'un client souscrive
            un contrat d'assurance auto — et optimiser la stratégie de contact marketing.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Key numbers ───────────────────────────────────────────────────────────
    cols = st.columns(4)
    cards = [
        ("Clients (train)",    "381 109",  "données d'entraînement"),
        ("Taux de souscription","12.3%",   "classe minoritaire"),
        ("Meilleur recall",    "93.8%",    "RF Randomized Search"),
        ("ROC AUC",            "85.6%",    "modèle final"),
    ]
    for col, (label, value, delta) in zip(cols, cards):
        col.markdown(metric_card(label, value, delta), unsafe_allow_html=True)

    # ── Pipeline steps ────────────────────────────────────────────────────────
    section_header("Pipeline du projet")

    steps = [
        ("Exploration des données",     "Analyse descriptive, détection des valeurs manquantes, visualisation des distributions et corrélations."),
        ("Feature Engineering",         "Discrétisation des âges, variables d'interaction, encodage ordinal/one-hot, standardisation multi-stratégie."),
        ("Modélisation",                "11 modèles testés : Random Forest, XGBoost, Gradient Boosting, LightGBM — avec Grid Search et Randomized Search."),
        ("Évaluation & sélection",      "Priorité au recall sur la classe positive (clients intéressés) compte tenu du fort déséquilibre des classes."),
        ("Production de résultats",     "Segmentation des clients en 3 zones (certain / incertain / improbable) et profilage de la zone cible."),
        ("Dashboard interactif",        "Application Streamlit couvrant l'ensemble du pipeline pour la prise de décision marketing."),
    ]

    col1, col2 = st.columns(2)
    for i, (title, desc) in enumerate(steps):
        target = col1 if i % 2 == 0 else col2
        with target:
            st.markdown(f"""
            <div class="step-item">
                <div class="step-num">{i+1}</div>
                <div class="step-body">
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
            </div>""", unsafe_allow_html=True)

    # ── Dataset description ───────────────────────────────────────────────────
    section_header("Description des variables")

    variables = {
        "id_client":           ("Identifiant",   "Identifiant unique du client"),
        "genre":               ("Catégorielle",  "Genre du client"),
        "age":                 ("Numérique",     "Âge du client"),
        "permis_conduire":     ("Binaire",       "Possession d'un permis (0/1)"),
        "code_regional":       ("Catégorielle",  "Région de résidence"),
        "ancien_assure":       ("Binaire",       "Déjà assuré par le passé (0/1)"),
        "age_vehicule":        ("Ordinale",      "Âge du véhicule : < 1 an, 1-2 ans, > 2 ans"),
        "vehicule_endommage":  ("Binaire",       "Véhicule déjà endommagé (0/1)"),
        "prime_annuelle":      ("Numérique",     "Montant de la prime annuelle (€)"),
        "canal_communication": ("Catégorielle",  "Canal de contact (mail, tél., internet…)"),
        "anciennete":          ("Numérique",     "Ancienneté client en jours"),
        "reponse_client":      ("Cible 🎯",      "0 = non intéressé · 1 = intéressé"),
    }

    rows_html = ""
    type_colors = {"Numérique":"badge-blue","Catégorielle":"badge-amber",
                   "Binaire":"badge-green","Ordinale":"badge-amber",
                   "Identifiant":"badge-gray","Cible 🎯":"badge-blue"}
    for var, (typ, desc) in variables.items():
        badge_cls = type_colors.get(typ, "badge-gray")
        rows_html += f"""
        <tr>
            <td><code style="background:#F1F5F9;padding:2px 6px;border-radius:4px;
                             font-size:0.8rem;font-family:'DM Mono',monospace">{var}</code></td>
            <td><span class="badge {badge_cls}">{typ}</span></td>
            <td style="color:#64748b">{desc}</td>
        </tr>"""

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr><th>Variable</th><th>Type</th><th>Description</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    insight_box("Le jeu de données présente un fort déséquilibre : seulement ~12% des clients sont intéressés par la souscription. Cette caractéristique a guidé le choix des métriques (recall, ROC AUC) et l'utilisation du paramètre <code>class_weight='balanced'</code>.")
