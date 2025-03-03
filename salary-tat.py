import streamlit as st
import pandas as pd

# GitHub file links
GITHUB_URL = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/IS.xlsx"
GITHUB_LOGO_URL = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/LOGO-Talent-Access-Technologies-removebg.png"

# Load IS data from GitHub
@st.cache_data
def charger_is_data():
    df = pd.read_excel(GITHUB_URL)
    df.columns = df.columns.str.strip()  # Remove extra spaces in column names
    return df

# Display Logo
st.image(GITHUB_LOGO_URL, width=200)

# LPP Contribution Table
LPP_TABLE = [
    (1, 25, 3.50, 0.70, 4.20),
    (2, 35, 5.00, 0.70, 5.70),
    (3, 45, 7.50, 1.20, 8.70),
    (4, 55, 9.00, 1.20, 10.20),
]

# Function to Get IS Rate from Excel
def obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df):
    tranche = is_df[(is_df["Année Min"] <= salaire_brut_annuel) & (is_df["Année Max"] >= salaire_brut_annuel)]
    if tranche.empty or statut_marital not in is_df.columns:
        return 0
    return tranche[statut_marital].values[0] / 100  # Convert to decimal

# Function to Get LPP Rate
def obtenir_taux_lpp(age):
    for row in LPP_TABLE:
        if row[1] == age:
            return row[4] / 100
    return 0

# Function to Calculate Net Salary
def calculer_salaire_net(salaire_brut_annuel, age, statut_marital, is_df, soumis_is):
    salaire_brut_mensuel = salaire_brut_annuel / 12
    taux_fixes = {
        "AVS": 5.3 / 100,
        "AC": 1.1 / 100,
        "AANP": 0.63 / 100,
        "Maternité": 0.032 / 100,
        "APG": 0.495 / 100,
        "Contribution professionnelle": 0.7 / 100,
    }
    cotisations = {key: salaire_brut_mensuel * taux for key, taux in taux_fixes.items()}
    cotisations["LPP"] = (salaire_brut_mensuel * obtenir_taux_lpp(age)) / 2

    # Ensure IS is only applied if subject to it
    if soumis_is:
        cotisations["Impôt Source"] = salaire_brut_mensuel * obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df)
    else:
        cotisations["Impôt Source"] = 0  # Ensure IS is NOT deducted

    total_deductions = sum(cotisations.values())
    salaire_net_mensuel = salaire_brut_mensuel - total_deductions
    return salaire_net_mensuel, cotisations

# Load IS Data
is_df = charger_is_data()

# Display Debug Info (Optional)
st.write("🔍 Debug: Column Names in IS.xlsx", list(is_df.columns))

# User Inputs
salaire_brut_annuel = st.number_input("💰 Salaire Brut Annuel (CHF)", min_value=0, value=120000)
age = st.number_input("🎂 Âge", min_value=25, max_value=65, value=35)

# Filter IS Columns (Remove unnecessary ones)
colonnes_a_exclure = ["Mois Max", "Unnamed: 5", "Unnamed: 6", "INDEX", "Année Min", "Année Max", "Mois Min"]
colonnes_filtrees = [col for col in is_df.columns if col not in colonnes_a_exclure]

# Marital Status Selection
situation_familiale = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", colonnes_filtrees)

# Residency Status Selection
nationalite = st.radio("🌍 Statut de résidence", ["🇨🇭 Suisse", "🏷️ Permis C", "🌍 Autre (Non imposé à la source)"])
soumis_is = nationalite in ["🇨🇭 Suisse", "🏷️ Permis C"]

# Calculate Salary
if st.button("🧮 Calculer"):
    salaire_net_mensuel, details_deductions = calculer_salaire_net(salaire_brut_annuel, age, situation_familiale, is_df, soumis_is)
    
    # Display Results
    st.write(f"### 💰 Salaire Net Mensuel : {salaire_net_mensuel:.2f} CHF")
    st.write("### 📉 Détail des Déductions :")
    for key, value in details_deductions.items():
        st.write(f"- **{key}** : {value:.2f} CHF")
