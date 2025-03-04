import streamlit as st
import pandas as pd

# URL du fichier IS.xlsx sur GitHub
GITHUB_URL_IS = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/IS.xlsx"

# URL du logo (Remplacez avec l'URL brute de votre logo sur GitHub)
GITHUB_LOGO_URL = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/LOGO-Talent-Access-Technologies-removebg.png"

# Charger les données Excel depuis GitHub
@st.cache_data
def charger_is_data():
    return pd.read_excel(GITHUB_URL_IS)

# Mise en page avec colonnes
col1, col2 = st.columns([3, 1])  # 75% - 25% pour l'affichage

# Affichage du logo à droite
with col2:
    st.image(GITHUB_LOGO_URL, width=200)

# Interface principale
with col1:
    st.title("📊 Calculateur de Salaire Net")

# Table des cotisations LPP
LPP_TABLE = [
    (1, 25, 3.50, 0.70, 4.20),
    (1, 26, 3.50, 0.70, 4.20),
    (1, 27, 3.50, 0.70, 4.20),
    (1, 28, 3.50, 0.70, 4.20),
    (1, 29, 3.50, 0.70, 4.20),
    (1, 30, 3.50, 0.70, 4.20),
    (1, 31, 3.50, 0.70, 4.20),
    (1, 32, 3.50, 0.70, 4.20),
    (1, 33, 3.50, 0.70, 4.20),
    (1, 34, 3.50, 0.70, 4.20),
    (2, 35, 5.00, 0.70, 5.70),
    (2, 36, 5.00, 0.70, 5.70),
    (2, 37, 5.00, 0.70, 5.70),
    (2, 38, 5.00, 0.70, 5.70),
    (2, 39, 5.00, 0.70, 5.70),
    (2, 40, 5.00, 0.70, 5.70),
    (2, 41, 5.00, 0.70, 5.70),
    (2, 42, 5.00, 0.70, 5.70),
    (2, 43, 5.00, 0.70, 5.70),
    (2, 44, 5.00, 0.70, 5.70),
    (3, 45, 7.50, 1.20, 8.70),
    (3, 46, 7.50, 1.20, 8.70),
    (3, 47, 7.50, 1.20, 8.70),
    (3, 48, 7.50, 1.20, 8.70),
    (3, 49, 7.50, 1.20, 8.70),
    (3, 50, 7.50, 1.20, 8.70),
    (3, 51, 7.50, 1.20, 8.70),
    (3, 52, 7.50, 1.20, 8.70),
    (3, 53, 7.50, 1.20, 8.70),
    (3, 54, 7.50, 1.20, 8.70),
    (4, 55, 9.00, 1.20, 10.20),
    (4, 56, 9.00, 1.20, 10.20),
    (4, 57, 9.00, 1.20, 10.20),
    (4, 58, 9.00, 1.20, 10.20),
    (4, 59, 9.00, 1.20, 10.20),
    (4, 60, 9.00, 1.20, 10.20),
    (4, 61, 9.00, 1.20, 10.20),
    (4, 62, 9.00, 1.20, 10.20),
    (4, 63, 9.00, 1.20, 10.20),
    (4, 64, 9.00, 1.20, 10.20),
    (4, 65, 9.00, 1.20, 10.20),
]

# Fonction pour obtenir le taux IS depuis Excel
def obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df):
    tranche = is_df[(is_df["Année Min"] <= salaire_brut_annuel) & (is_df["Année Max"] >= salaire_brut_annuel)]
    if tranche.empty or statut_marital not in is_df.columns:
        return 0
    return tranche[statut_marital].values[0] / 100

# Fonction pour obtenir le taux LPP
def obtenir_taux_lpp(age):
    for row in LPP_TABLE:
        if row[1] == age:
            return row[4] / 100
    return 0

# Fonction principale de calcul du salaire net
def calculer_salaire_net(salaire_brut_annuel, age, statut_marital, is_df, soumis_is):
    salaire_brut_mensuel = salaire_brut_annuel / 12
    taux_fixes = {
        "AVS": 5.3 / 100,
        "AC": 1.1 / 100,
        "AANP": 0.63 / 100,
        "Maternité": 0.032 / 100,
        "APG": 0.495 / 100,
    }
    cotisations = {key: salaire_brut_mensuel * taux for key, taux in taux_fixes.items()}
    cotisations["LPP"] = (salaire_brut_mensuel * obtenir_taux_lpp(age))/2

    # Appliquer l'IS seulement si soumis à l'impôt à la source
    if soumis_is:
        cotisations["Impôt Source"] = salaire_brut_mensuel * obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df)
    
    total_deductions = sum(cotisations.values())
    salaire_net_mensuel = salaire_brut_mensuel - total_deductions
    return salaire_net_mensuel, cotisations

# Chargement des données IS.xlsx
is_df = charger_is_data()
colonnes_filtrees = [col for col in is_df.columns if col not in ["Mois Max", "Unnamed: 5", "Unnamed: 6"]]

# Entrées utilisateur
salaire_brut_annuel = st.number_input("💰 Salaire Brut Annuel (CHF)", min_value=0, value=160000)
age = st.number_input("🎂 Âge", min_value=25, max_value=65, value=35)
situation_familiale = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", colonnes_filtrees[4:])

# Sélection du statut de résidence
nationalite = st.radio("🌍 Statut de résidence", ["🇨🇭 Suisse", "🏷️ Permis C", "🌍 Autre (Imposé à la source)"])
soumis_is = nationalite == "🌍 Autre (Imposé à la source)"

# Bouton de calcul
if st.button("🧮 Calculer"):
    salaire_net_mensuel, details_deductions = calculer_salaire_net(salaire_brut_annuel, age, situation_familiale, is_df, soumis_is)
    st.write(f"### 💰 Salaire Net Mensuel : {salaire_net_mensuel:.2f} CHF")
    st.write("### 📉 Détail des Déductions :")
    for key, value in details_deductions.items():
        st.write(f"- **{key}** : {value:.2f} CHF")

# 🔹 **Section Calcul de la Marge et TJM Minimum**
st.header("📊 Calcul de la Marge & TJM Minimum")

# Entrées utilisateur pour la marge
tjm_client = st.number_input("💰 TJM Client (CHF)", min_value=0, value=800)
jours_travailles = st.number_input("📅 Nombre de jours travaillés par mois", min_value=1, max_value=30, value=20)

# Bouton de calcul du TJM
if st.button("📈 Calculer TJM Minimum"):
    if st.session_state["salaire_brut_mensuel"] is not None:
        salaire_brut_mensuel = st.session_state["salaire_brut_mensuel"]
        revenus_mensuels = tjm_client * jours_travailles
        tjm_minimum = (salaire_brut_mensuel / 0.7) / jours_travailles  # Marge de 30%
        marge_actuelle = (revenus_mensuels - salaire_brut_mensuel) / revenus_mensuels * 100

        st.write(f"### 📉 Marge Actuelle : {marge_actuelle:.2f} %")
        st.write(f"### ⚠️ TJM Minimum à respecter pour 30% de marge : {tjm_minimum:.2f} CHF")

        if tjm_client >= tjm_minimum:
            st.success("✅ Votre TJM couvre la marge requise de 30%")
        else:
            st.warning("⚠️ Votre TJM est trop bas pour assurer une marge de 30%")
    else:
        st.warning("⚠️ Veuillez d'abord calculer le salaire avant d'estimer la marge.")
