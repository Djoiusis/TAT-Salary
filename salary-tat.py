import streamlit as st
import pandas as pd

# URL du fichier IS.xlsx sur GitHub (Assurez-vous que c'est bien l'URL brute !)
GITHUB_URL = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/IS.xlsx"

GITHUB_LOGO_URL = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/LOGO-Talent-Access-Technologies-removebg.png"


# Charger les données Excel depuis GitHub
@st.cache_data
def charger_is_data():
    return pd.read_excel(GITHUB_URL)

# Affichage du logo
st.image(GITHUB_LOGO_URL, width=200)  # Ajustez la largeur si nécessaire

# Table des cotisations LPP (conservée en dur)
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
def calculer_salaire_net(salaire_brut_annuel, age, statut_marital, is_df):
    salaire_brut_mensuel = salaire_brut_annuel / 12
    taux_fixes = {
        "AVS": 5.3 / 100,
        "AC": 1.1 / 100,
        "AANP": 0.63 / 100,
        "Maternité": 0.032 / 100,
        "APG": 0.495 / 100,
        "Contribution professionnelle": 0.7/100,
    }
    cotisations = {key: salaire_brut_mensuel * taux for key, taux in taux_fixes.items()}
    cotisations["LPP"] = (salaire_brut_mensuel * obtenir_taux_lpp(age))/2
    cotisations["Impôt Source"] = salaire_brut_mensuel * obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df)
    total_deductions = sum(cotisations.values())
    salaire_net_mensuel = salaire_brut_mensuel - total_deductions
    return salaire_net_mensuel, cotisations

# Interface Streamlit
st.title("📊 Calculateur de Salaire Net")

# Chargement des données IS.xlsx
is_df = charger_is_data()

# Entrées utilisateur
salaire_brut_annuel = st.number_input("💰 Salaire Brut Annuel (CHF)", min_value=0, value=160000)
age = st.number_input("🎂 Âge", min_value=25, max_value=65, value=35)

# Sélection du statut marital basé sur les colonnes du fichier Excel
situation_familiale = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", is_df.columns[4:])

# Bouton de calcul
if st.button("🧮 Calculer"):
    salaire_net_mensuel, details_deductions = calculer_salaire_net(salaire_brut_annuel, age, situation_familiale, is_df)
    
    # Résultats
    st.write(f"### 💰 Salaire Net Mensuel : {salaire_net_mensuel:.2f} CHF")
    st.write("### 📉 Détail des Déductions :")
    for key, value in details_deductions.items():
        st.write(f"- **{key}** : {value:.2f} CHF")
