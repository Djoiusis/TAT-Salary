import streamlit as st
import pandas as pd

# Charger les données Excel sous forme de dictionnaire de DataFrames
@st.cache_data
def charger_donnees(fichier):
    xls = pd.ExcelFile(fichier)
    return {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}

# Déterminer le taux LPP en fonction de l'âge
def obtenir_taux_lpp(age, lpp_df):
    for _, row in lpp_df.iterrows():
        age_min, age_max = map(int, row["Âge LPP"].split('-'))
        if age_min <= age <= age_max:
            return row["Total LPP"] / 100
    return 0

# Déterminer le taux IS selon le salaire brut et le statut marital
def obtenir_taux_is(salaire_brut, statut_marital, is_df):
    statut_ligne = is_df[is_df["Statut Marital"] == statut_marital]
    
    if statut_ligne.empty:
        return 0
    
    statut_ligne = statut_ligne.sort_values(by="Salaire Min", ascending=True)
    
    for _, row in statut_ligne.iterrows():
        if salaire_brut >= row["Salaire Min"] and salaire_brut <= row["Salaire Max"]:
            return row["Taux IS"] / 100

    return 0

# Fonction principale de calcul du salaire net
def calculer_salaire_net(salaire_brut, age, statut_marital, lpp_df, is_df):
    # Taux fixes des cotisations sociales
    taux_avs = 5.3 / 100
    taux_ac = 1.1 / 100
    taux_aanp = 0.63 / 100
    taux_maternite = 0.032 / 100
    taux_apg = 0.495 / 100

    # Calcul des cotisations sociales
    cotisation_avs = salaire_brut * taux_avs
    cotisation_ac = salaire_brut * taux_ac
    cotisation_aanp = salaire_brut * taux_aanp
    cotisation_maternite = salaire_brut * taux_maternite
    cotisation_apg = salaire_brut * taux_apg

    # Calcul de la cotisation LPP selon l'âge
    taux_lpp = obtenir_taux_lpp(age, lpp_df)
    cotisation_lpp = salaire_brut * taux_lpp

    # Calcul du taux IS automatique
    taux_is = obtenir_taux_is(salaire_brut, statut_marital, is_df)
    impot_source = salaire_brut * taux_is

    # Total des déductions
    total_deductions = (
        cotisation_avs + cotisation_ac + cotisation_aanp +
        cotisation_maternite + cotisation_apg + cotisation_lpp + impot_source
    )

    # Calcul du salaire net
    salaire_net = salaire_brut - total_deductions

    return salaire_net, taux_is * 100, {
        "Retenue AVS": cotisation_avs,
        "Cotisations AC": cotisation_ac,
        "Assurance maternité": cotisation_maternite,
        "Cotisations AANP": cotisation_aanp,
        "Caisse de pension LPP": cotisation_lpp,
        "Cotisations APG mal": cotisation_apg,
        "Retenue impôt à la source": impot_source,
        "Total Déductions": total_deductions,
        "Salaire Net": salaire_net
    }

# Interface Streamlit
st.title("Calculateur de Salaire Net 💰")

# Upload du fichier Excel
fichier_excel = st.file_uploader("Téléchargez le fichier Excel", type=["xlsx"])
if fichier_excel:
    donnees = charger_donnees(fichier_excel)

    # Chargement des données
    lpp_df = donnees["LPP"]
    is_df = donnees["ImpotSource"]

    # Entrée utilisateur
    salaire_brut = st.number_input("Salaire Brut (CHF)", min_value=0, value=13333)
    age = st.number_input("Âge", min_value=18, max_value=65, value=35)

    # Liste déroulante pour choisir la situation familiale
    situation_familiale = st.selectbox("Situation familiale", options=[
        "Célibataire sans enfant",
        "Marié et le conjoint ne travaille pas et 0 enfant",
        "Marié et le conjoint ne travaille pas et 1 enfant",
        "Marié et le conjoint ne travaille pas et 2 enfants",
        "Marié et le conjoint ne travaille pas et 3 enfants",
        "Marié et le conjoint ne travaille pas et 4 enfants",
        "Marié et le conjoint ne travaille pas et 5 enfants",
        "Marié et les 2 conjoints travaillent et 0 enfant",
        "Marié et les 2 conjoints travaillent et 1 enfant",
        "Marié et les 2 conjoints travaillent et 2 enfants",
        "Marié et les 2 conjoints travaillent et 3 enfants",
        "Marié et les 2 conjoints travaillent et 4 enfants",
        "Marié et les 2 conjoints travaillent et 5 enfants",
        "Famille monoparentale et 1 enfant",
        "Famille monoparentale et 2 enfants",
        "Famille monoparentale et 3 enfants",
        "Famille monoparentale et 4 enfants",
        "Famille monoparentale et 5 enfants"
    ])

    if st.button("Calculer"):
        salaire_net, taux_is, details = calculer_salaire_net(salaire_brut, age, situation_familiale, lpp_df, is_df)

        # Affichage des résultats
        st.write(f"### Salaire Net : {salaire_net:.2f} CHF")
        st.write(f"### Taux IS Calculé : {taux_is:.2f} %")
        st.write("### Détails des Déductions :")
        for key, value in details.items():
            st.write(f"- **{key}** : {value:.2f} CHF")
