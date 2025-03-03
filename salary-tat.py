import streamlit as st
import pandas as pd

# Charger les données Excel sous forme de dictionnaire de DataFrames
@st.cache_data
def charger_donnees(fichier):
    xls = pd.ExcelFile(fichier)
    return {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}

# Fonction pour obtenir le taux LPP
def obtenir_taux_lpp(age, lpp_df):
    taux_lpp = lpp_df.loc[lpp_df["Age"] == age, "Total (%)"]
    return taux_lpp.values[0] / 100 if not taux_lpp.empty else 0

# Fonction pour obtenir le taux IS depuis le fichier IS.xlsx
def obtenir_taux_is(salaire_brut, statut_marital, is_df):
    statut_ligne = is_df[is_df["Statut Marital"] == statut_marital]
    
    if statut_ligne.empty:
        return 0  # Retourne 0 si le statut n'existe pas

    # Trier les valeurs selon les salaires minimaux
    statut_ligne = statut_ligne.sort_values(by="Salaire Min", ascending=True)
    
    for _, row in statut_ligne.iterrows():
        if salaire_brut >= row["Salaire Min"] and salaire_brut <= row["Salaire Max"]:
            return row["Taux IS"] / 100

    return 0  # Retourne 0 si aucun taux trouvé

# Fonction principale de calcul du salaire net
def calculer_salaire_net(salaire_brut_annuel, age, statut_marital, lpp_df, is_df):
    salaire_brut_mensuel = salaire_brut_annuel / 12

    # Taux fixes des cotisations sociales
    taux_avs = 5.3 / 100
    taux_ac = 1.1 / 100
    taux_aanp = 0.63 / 100
    taux_maternite = 0.032 / 100
    taux_apg = 0.495 / 100

    # Calcul des cotisations sociales
    cotisation_avs = salaire_brut_mensuel * taux_avs
    cotisation_ac = salaire_brut_mensuel * taux_ac
    cotisation_aanp = salaire_brut_mensuel * taux_aanp
    cotisation_maternite = salaire_brut_mensuel * taux_maternite
    cotisation_apg = salaire_brut_mensuel * taux_apg

    # Calcul de la cotisation LPP selon l'âge
    taux_lpp = obtenir_taux_lpp(age, lpp_df)
    cotisation_lpp = salaire_brut_mensuel * taux_lpp

    # Calcul du taux IS depuis IS.xlsx
    taux_is = obtenir_taux_is(salaire_brut_annuel, statut_marital, is_df)
    impot_source = salaire_brut_mensuel * taux_is

    # Total des déductions
    total_deductions = (
        cotisation_avs + cotisation_ac + cotisation_aanp +
        cotisation_maternite + cotisation_apg + cotisation_lpp + impot_source
    )

    # Calcul du salaire net mensuel
    salaire_net_mensuel = salaire_brut_mensuel - total_deductions

    return salaire_net_mensuel, taux_is * 100, {
        "Retenue AVS": cotisation_avs,
        "Cotisations AC": cotisation_ac,
        "Assurance maternité": cotisation_maternite,
        "Cotisations AANP": cotisation_aanp,
        "Caisse de pension LPP": cotisation_lpp,
        "Cotisations APG mal": cotisation_apg,
        "Retenue impôt à la source": impot_source,
        "Total Déductions": total_deductions,
        "Salaire Net Mensuel": salaire_net_mensuel
    }

# Interface Streamlit
st.title("Calculateur de Salaire Net 💰")

# Upload du fichier IS.xlsx
fichier_excel = st.file_uploader("📂 Téléchargez le fichier IS.xlsx", type=["xlsx"])
if fichier_excel:
    donnees = charger_donnees(fichier_excel)

    # Chargement des données depuis IS.xlsx
    is_df = donnees[list(donnees.keys())[0]]  # On prend la première feuille
    lpp_df = None  # Si nécessaire, on ajoutera un fichier pour les taux LPP

    # Entrée utilisateur
    salaire_brut_annuel = st.number_input("💰 Salaire Brut Annuel (CHF)", min_value=0, value=160000)
    age = st.number_input("🎂 Âge", min_value=25, max_value=65, value=35)

    # Liste déroulante pour choisir la situation familiale (depuis IS.xlsx)
    situation_familiale = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", options=is_df["Statut Marital"].unique())

    if st.button("🧮 Calculer"):
        salaire_net_mensuel, taux_is, details = calculer_salaire_net(salaire_brut_annuel, age, situation_familiale, lpp_df, is_df)

        # Affichage des résultats
        st.write(f"### 💰 Salaire Net Mensuel : {salaire_net_mensuel:.2f} CHF")
        st.write(f"### 📊 Taux IS Calculé : {taux_is:.2f} %")
        st.write("### 📋 Détails des Déductions :")
        for key, value in details.items():
            st.write(f"- **{key}** : {value:.2f} CHF")
