import streamlit as st
import pandas as pd

GITHUB_URL = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/IS.xlsx"

# Charger les données Excel (IS.xlsx)
@st.cache_data
def charger_is_data(fichier):
    return pd.read_excel(GITHUB_URL)

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

# Fonction pour obtenir le taux IS depuis le fichier Excel
def obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df):
    tranche = is_df[(is_df["Année Min"] <= salaire_brut_annuel) & (is_df["Année Max"] >= salaire_brut_annuel)]
    if tranche.empty:
        return 0
    return tranche[statut_marital].values[0] / 100 if statut_marital in is_df.columns else 0

# Fonction pour obtenir le taux LPP
def obtenir_taux_lpp(age):
    for row in LPP_TABLE:
        if row[1] == age:
            return row[4] / 100
    return 0

# Fonction principale avec détails
def calculer_salaire_net(salaire_brut_annuel, age, statut_marital, is_df):
    salaire_brut_mensuel = salaire_brut_annuel / 12

    taux_avs = 5.3 / 100
    taux_ac = 1.1 / 100
    taux_aanp = 0.63 / 100
    taux_maternite = 0.032 / 100
    taux_apg = 0.495 / 100

    cotisation_avs = salaire_brut_mensuel * taux_avs
    cotisation_ac = salaire_brut_mensuel * taux_ac
    cotisation_aanp = salaire_brut_mensuel * taux_aanp
    cotisation_maternite = salaire_brut_mensuel * taux_maternite
    cotisation_apg = salaire_brut_mensuel * taux_apg

    taux_lpp = obtenir_taux_lpp(age)
    cotisation_lpp = (salaire_brut_mensuel * taux_lpp)/2

    taux_is = obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df)
    impot_source = salaire_brut_mensuel * taux_is

    total_deductions = (
        cotisation_avs + cotisation_ac + cotisation_aanp +
        cotisation_maternite + cotisation_apg + cotisation_lpp + impot_source
    )

    salaire_net_mensuel = salaire_brut_mensuel - total_deductions

    details = {
        "Retenue AVS": cotisation_avs,
        "Cotisations AC": cotisation_ac,
        "Assurance maternité": cotisation_maternite,
        "Cotisations AANP": cotisation_aanp,
        "Caisse de pension LPP": cotisation_lpp,
        "Cotisations APG mal": cotisation_apg,
        "Retenue impôt à la source": impot_source,
        "Total Déductions": total_deductions,
    }

    return salaire_net_mensuel, details

# Interface Streamlit
st.title("Calculateur de Salaire Net 💰")

fichier_excel = st.file_uploader("📂 Téléchargez le fichier IS.xlsx", type=["xlsx"])
if fichier_excel:
    is_df = charger_is_data(fichier_excel)

    salaire_brut_annuel = st.number_input("💰 Salaire Brut Annuel (CHF)", min_value=0, value=160000)
    age = st.number_input("🎂 Âge", min_value=25, max_value=65, value=35)

    situation_familiale = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", is_df.columns[4:])

    if st.button("🧮 Calculer"):
        salaire_net_mensuel, details = calculer_salaire_net(salaire_brut_annuel, age, situation_familiale, is_df)
        st.write(f"### 💰 Salaire Net Mensuel : {salaire_net_mensuel:.2f} CHF")

        st.write("### 📋 Détails des Déductions :")
        for key, value in details.items():
            st.write(f"- **{key}** : {value:.2f} CHF")
