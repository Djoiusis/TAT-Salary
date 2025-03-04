import streamlit as st
import pandas as pd

# URL du fichier IS.xlsx sur GitHub
GITHUB_URL_IS = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/IS.xlsx"

# URL du logo
GITHUB_LOGO_URL = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/LOGO-Talent-Access-Technologies-removebg.png"

# Charger les données Excel depuis GitHub
@st.cache_data
def charger_is_data():
    return pd.read_excel(GITHUB_URL_IS)

# 🌟 **Affichage du Logo Centré**
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="{GITHUB_LOGO_URL}" width="250">
    </div>
    """,
    unsafe_allow_html=True
)

# **Table des cotisations LPP**
LPP_TABLE = [
    (1, 25, 3.50, 0.70, 4.20),
    (2, 35, 5.00, 0.70, 5.70),
    (3, 45, 7.50, 1.20, 8.70),
    (4, 55, 9.00, 1.20, 10.20),
]

# **Fonction pour obtenir le taux IS**
def obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df):
    tranche = is_df[(is_df["Année Min"] <= salaire_brut_annuel) & (is_df["Année Max"] >= salaire_brut_annuel)]
    if tranche.empty or statut_marital not in is_df.columns:
        return 0
    return tranche[statut_marital].values[0] / 100

# **Fonction pour obtenir le taux LPP**
def obtenir_taux_lpp(age):
    for row in LPP_TABLE:
        if row[1] <= age < (row[1] + 10):
            return row[4] / 100
    return 0

# **Fonction principale de calcul du salaire net**
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
    cotisations["LPP"] = (salaire_brut_mensuel * obtenir_taux_lpp(age)) / 2

    # Appliquer l'IS seulement si soumis à l'impôt à la source
    cotisations["Impôt Source"] = 0
    if soumis_is:
        cotisations["Impôt Source"] = salaire_brut_mensuel * obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df)
    
    total_deductions = sum(cotisations.values())
    salaire_net_mensuel = salaire_brut_mensuel - total_deductions

    return salaire_net_mensuel, cotisations

# **Chargement des données IS.xlsx**
is_df = charger_is_data()

# **Supprimer les colonnes inutiles**
colonnes_a_exclure = ["Mois Max", "Unnamed: 5", "Unnamed: 6", "INDEX", "Année Min", "Année Max", "Mois Min"]
colonnes_filtrees = [col for col in is_df.columns if col not in colonnes_a_exclure]

# **💰 Calcul du Salaire Net**
st.header("💰 Calcul du Salaire Net")

# **Entrées utilisateur**
salaire_brut_annuel = st.number_input("💰 Salaire Brut Annuel (CHF)", min_value=0, value=160000)
age = st.number_input("🎂 Âge", min_value=25, max_value=65, value=35)
situation_familiale = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", colonnes_filtrees[4:])

# **Sélection du statut de résidence**
nationalite = st.radio("🌍 Statut de résidence", ["🇨🇭 Suisse", "🏷️ Permis C", "🌍 Autre (Imposé à la source)"])
soumis_is = nationalite == "🌍 Autre (Imposé à la source)"

# **Bouton de calcul**
if st.button("🧮 Calculer Salaire"):
    salaire_net_mensuel, details_deductions = calculer_salaire_net(
        salaire_brut_annuel, age, situation_familiale, is_df, soumis_is
    )

    st.write(f"### 💰 Salaire Net Mensuel : {salaire_net_mensuel:.2f} CHF")
    st.write("### 📉 Détail des Déductions :")
    for key, value in details_deductions.items():
        st.write(f"- **{key}** : {value:.2f} CHF")
