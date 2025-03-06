import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# 📌 URL du fichier IS.xlsx sur GitHub
GITHUB_URL_IS = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/IS.xlsx"

# 📌 URL du logo
GITHUB_LOGO_URL = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/LOGO-Talent-Access-Technologies-removebg.png"

# 📌 Charger les données Excel depuis GitHub
@st.cache_data
def charger_is_data():
    response = requests.get(GITHUB_URL_IS)
    if response.status_code == 200:
        return pd.read_excel(BytesIO(response.content), engine="openpyxl")
    else:
        st.error("❌ Erreur : Impossible de télécharger le fichier Excel.")
        return None

# 📌 **Ajout du style CSS pour améliorer la lisibilité**
st.markdown(
    f"""
    <style>
        .stApp {{
            background: url("https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/background.jpg") no-repeat center center fixed;
            background-size: cover;
        }}

        .block {{
            background-color: rgba(0, 0, 0, 0.8);
            padding: 25px;
            border-radius: 15px;
            color: white;
            box-shadow: 0px 0px 15px rgba(255, 255, 255, 0.2);
        }}

        .title {{
            text-align: center;
            font-size: 30px;
            font-weight: bold;
            color: white;
            text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.7);
        }}

        .spacer {{
            margin-top: 40px;
            margin-bottom: 40px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# 📌 **Affichage du Logo Centré**
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="{GITHUB_LOGO_URL}" width="250">
    </div>
    """,
    unsafe_allow_html=True
)

# 📌 **Chargement des données IS.xlsx**
is_df = charger_is_data()
if is_df is None:
    st.stop()

# 📌 **Espacement avant la mise en page**
st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

# 📌 **Mise en page en deux colonnes**
col1, col2 = st.columns(2)

# 🔹 **Colonne 1 : Calcul du Salaire Net**
with col1:
    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.header("💰 Calcul du Salaire Net")

    # **Entrées utilisateur**
    salaire_brut_annuel = st.number_input("💰 Salaire Brut Annuel (CHF)", min_value=0, value=160000)
    age = st.number_input("🎂 Âge", min_value=25, max_value=65, value=35)

    # **Sélection de la situation familiale**
    colonnes_a_exclure = ["Mois Max", "Unnamed: 5", "Unnamed: 6", "INDEX", "Année Min", "Année Max", "Mois Min"]
    colonnes_filtrees = [col for col in is_df.columns if col not in colonnes_a_exclure]
    situation_familiale = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", colonnes_filtrees[4:])

    # **Sélection du statut de résidence**
    nationalite = st.radio("🌍 Statut de résidence", ["🇨🇭 Suisse", "🏷️ Permis C", "🌍 Autre (Imposé à la source)"])
    soumis_is = nationalite == "🌍 Autre (Imposé à la source)"

    # **Bouton de calcul**
    if st.button("🧮 Calculer Salaire"):
        salaire_brut_mensuel = salaire_brut_annuel / 12
        taux_is = 0 if not soumis_is else (is_df[situation_familiale].loc[
            (is_df["Année Min"] <= salaire_brut_annuel) & (is_df["Année Max"] >= salaire_brut_annuel)
        ].values[0] / 100)

        # **Calcul des cotisations**
        taux_fixes = {
            "AVS": 5.3 / 100,
            "AC": 1.1 / 100,
            "AANP": 0.63 / 100,
            "Maternité": 0.032 / 100,
            "APG": 0.495 / 100,
        }
        cotisations = {key: salaire_brut_mensuel * taux for key, taux in taux_fixes.items()}
        cotisations["Impôt Source"] = salaire_brut_mensuel * taux_is

        total_deductions = sum(cotisations.values())
        salaire_net_mensuel = salaire_brut_mensuel - total_deductions

        st.write(f"### 💰 Salaire Net Mensuel : {salaire_net_mensuel:.2f} CHF")
        st.write("### 📉 Détail des Déductions :")
        for key, value in cotisations.items():
            st.write(f"- **{key}** : {value:.2f} CHF")

    st.markdown('</div>', unsafe_allow_html=True)

# 🌟 **Espacement entre les blocs**
st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

# 🔹 **Colonne 2 : Simulation Portage Salarial**
with col2:
    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.header("💼 Simulation Portage Salarial")

    # **Entrées utilisateur pour le portage**
    tjm_client = st.number_input("💰 TJM Client (CHF)", min_value=0, value=800)
    jours_travailles = st.number_input("📅 Jours travaillés par mois", min_value=1, max_value=30, value=20)

    # **Charges employeur en portage**
    charges_employeur = {
        "AVS": 5.3 / 100,
        "AC": 1.1 / 100,
        "Alloc. Familiale": 2.25 / 100,
        "Petite Enfance": 0.07 / 100,
        "LFP": 0.082 / 100,
        "Amat": 0.032 / 100,
        "AAP": 0.0476 / 100,
        "APG": 0.48 / 100,
    }

    # **Calcul du salaire net en portage**
    if st.button("📈 Simuler Portage Salarial"):
        revenus_mensuels = tjm_client * jours_travailles
        cout_employeur_total = sum(revenus_mensuels * taux for taux in charges_employeur.values())

        salaire_net_portage = revenus_mensuels - cout_employeur_total

        st.write(f"### 📉 Salaire Net en Portage Salarial : {salaire_net_portage:.2f} CHF")
        st.write("### 📋 Détail des Charges Employeur :")
        for key, value in charges_employeur.items():
            st.write(f"- **{key}** : {revenus_mensuels * value:.2f} CHF")

    st.markdown('</div>', unsafe_allow_html=True)
