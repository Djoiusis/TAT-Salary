import streamlit as st
import requests
import openpyxl
from io import BytesIO
import pandas as pd

# Dictionnaire de correspondance global
correspondance_situation = {
    "Célibataire sans enfant": "Célibataire 0",
    "Marié et le conjoint ne travaille pas et 0 enfant": "Marié et le conjoint ne travaille pas 0",
    "Marié et le conjoint ne travaille pas et 1 enfant": "Marié et le conjoint ne travaille pas 1",
    "Marié et le conjoint ne travaille pas et 2 enfants": "Marié et le conjoint ne travaille pas 2",
    "Marié et le conjoint ne travaille pas et 3 enfants": "Marié et le conjoint ne travaille pas 3",
    "Marié et le conjoint ne travaille pas et 4 enfants": "Marié et le conjoint ne travaille pas 4",
    "Marié et le conjoint ne travaille pas et 5 enfants": "Marié et le conjoint ne travaille pas 5",
    "Marié et les 2 conjoints travaillent et 0 enfant": "Marié et les 2 conjoints travaillent 0",
    "Marié et les 2 conjoints travaillent et 1 enfant": "Marié et les 2 conjoints travaillent 1",
    "Marié et les 2 conjoints travaillent et 2 enfants": "Marié et les 2 conjoints travaillent 2",
    "Marié et les 2 conjoints travaillent et 3 enfants": "Marié et les 2 conjoints travaillent 3",
    "Marié et les 2 conjoints travaillent et 4 enfants": "Marié et les 2 conjoints travaillent 4",
    "Marié et les 2 conjoints travaillent et 5 enfants": "Marié et les 2 conjoints travaillent 5",
    "Famille monoparentale et 1 enfant": "Famille monoparentale 1",
    "Famille monoparentale et 2 enfants": "Famille monoparentale 2",
    "Famille monoparentale et 3 enfants": "Famille monoparentale 3",
    "Famille monoparentale et 4 enfants": "Famille monoparentale 4",
    "Famille monoparentale et 5 enfants": "Famille monoparentale 5",
}


# Fonction pour charger et nettoyer les données LPP et impôts
def load_data():
    url = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/Salaires_Tarifs_TAT.xlsx"
    
    # Télécharger le fichier depuis GitHub
    response = requests.get(url)
    
    if response.status_code != 200:
        raise ValueError("Erreur lors du téléchargement du fichier Excel")

    # Charger le fichier dans Pandas depuis la mémoire
    xls = pd.ExcelFile(BytesIO(response.content))
    
    lpp_data = pd.read_excel(xls, sheet_name="LPP")
    impots_data = pd.read_excel(xls, sheet_name="Impôts", header=1)
    
    # Nettoyage des données (simplifié)
    lpp_data = lpp_data.dropna(how='all').reset_index(drop=True)
    
    # Fusionner la deuxième et la troisième ligne pour recréer les noms corrects
    impots_data.columns = impots_data.iloc[0].astype(str).fillna('') + " " + impots_data.iloc[1].astype(str).fillna('')
    impots_data = impots_data[2:].reset_index(drop=True)
    
    # Nettoyer les noms de colonnes
    impots_data.columns = impots_data.columns.str.replace(r'\.0$', '', regex=True).str.strip()
    
    return lpp_data, impots_data

# Fonction pour calculer le salaire net
def calculer_salaire_net(salaire_brut, age, situation_familiale, lpp_data, impots_data):
    correspondance_age_lpp = {
        "25-34 ans": "1",
        "35-44 ans": "2",
        "45-54 ans": "3",
        "55-65 ans": "4"
    }

    categorie_age = correspondance_age_lpp.get(age)
    if categorie_age is None:
        raise ValueError(f"L'âge sélectionné ({age}) n'existe pas dans la correspondance.")

    lpp_data.iloc[:, 2] = lpp_data.iloc[:, 2].astype(str).str.strip()
    matching_rows = lpp_data[lpp_data.iloc[:, 2] == categorie_age]

    if matching_rows.empty:
        raise ValueError(f"Aucune correspondance trouvée pour l'âge : {age} (Catégorie {categorie_age}).")

    taux_lpp = matching_rows.iloc[0, 3]
    cotisation_lpp = salaire_brut * taux_lpp
    print(type(salaire_net), salaire_net)


    
    colonne_impot = correspondance_situation.get(situation_familiale)
    if colonne_impot not in impots_data.columns:
        raise ValueError(f"La colonne pour {situation_familiale} ({colonne_impot}) n'existe pas dans les impôts. Vérifiez : {impots_data.columns.tolist()}")
    
    impots_row = impots_data[(impots_data.iloc[:, 1] <= salaire_brut) & (impots_data.iloc[:, 2] >= salaire_brut)]
    taux_impot = impots_row[colonne_impot].values[0] if not impots_row.empty else 0
    impot = salaire_brut * (taux_impot / 100)

    salaire_brut = float(salaire_brut)
    cotisation_lpp = float(cotisation_lpp)
    impot = float(impot)
    
    salaire_net = salaire_brut - cotisation_lpp - impot
    return salaire_net

# Interface utilisateur avec Streamlit
st.title("Calculateur de Salaire Net")

salaire_brut = st.number_input("Salaire brut mensuel (CHF)", min_value=0, step=100)
age = st.selectbox("Âge", options=["25-34 ans", "35-44 ans", "45-54 ans", "55-65 ans"])
situation_familiale = st.selectbox("Situation familiale", options=list(correspondance_situation.keys()))


if st.button("Calculer Salaire Net"):
    lpp_data, impots_data = load_data()
    salaire_net = calculer_salaire_net(salaire_brut, age, situation_familiale, lpp_data, impots_data)
    st.success(f"Votre salaire net estimé est de : {salaire_net:.2f} CHF")
