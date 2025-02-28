import streamlit as st
import requests
import openpyxl
from io import BytesIO
import pandas as pd

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
    # Recharger les impôts avec la bonne ligne d'en-tête (ligne 2 du fichier, index 1)
    impots_data = pd.read_excel(xls, sheet_name="Impôts", header=1)

    # Fusionner les deux premières lignes pour recréer des noms de colonnes corrects
    impots_data.columns = impots_data.iloc[0].astype(str) + " " + impots_data.iloc[1].astype(str)
    impots_data = impots_data[2:].reset_index(drop=True)  # Supprimer les lignes en double après fusion

    # Afficher les nouveaux noms des colonnes
    st.write("Noms des colonnes après correction :", impots_data.columns.tolist())

    
    return lpp_data, impots_data

# Fonction pour calculer le salaire net
def calculer_salaire_net(salaire_brut, age, situation_familiale, lpp_data, impots_data):
    st.write("Noms des colonnes dans impôts :", impots_data.columns.tolist())
    st.write("Situation familiale sélectionnée :", situation_familiale)

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
    
    colonne_impot = impots_data.columns[impots_data.iloc[0] == situation_familiale].values[0]
    impots_row = impots_data[(impots_data.iloc[:, 1] <= salaire_brut) & (impots_data.iloc[:, 2] >= salaire_brut)]
    taux_impot = impots_row[colonne_impot].values[0] if not impots_row.empty else 0
    impot = salaire_brut * (taux_impot / 100)
    
    salaire_net = salaire_brut - cotisation_lpp - impot
    return salaire_net

# Interface utilisateur avec Streamlit
st.title("Calculateur de Salaire Net")

salaire_brut = st.number_input("Salaire brut mensuel (CHF)", min_value=0, step=100)
age = st.selectbox("Âge", options=["25-34 ans", "35-44 ans", "45-54 ans", "55-65 ans"])
situation_familiale = st.selectbox("Situation familiale", options=["Célibataire sans enfant", "Marié et le conjoint ne travaille pas et 0 enfant", "Marié et le conjoint ne travaille pas et 1 enfant", "Marié et le conjoint ne travaille pas et 2 enfants", "Marié et le conjoint ne travaille pas et 3 enfants", "Marié et le conjoint ne travaille pas et 4 enfants", "Marié et le conjoint ne travaille pas et 5 enfants", "Marié et les 2 conjoints travaillent et 0 enfant", "Marié et les 2 conjoints travaillent et 1 enfant", "Marié et les 2 conjoints travaillent et 2 enfants", "Marié et les 2 conjoints travaillent et 3 enfants", "Marié et les 2 conjoints travaillent et 4 enfants", "Marié et les 2 conjoints travaillent et 5 enfants", "Famille monoparentale et 1 enfant", "Famille monoparentale et 2 enfants", "Famille monoparentale et 3 enfants", "Famille monoparentale et 4 enfants", "Famille monoparentale et 5 enfants"])

if st.button("Calculer Salaire Net"):
    lpp_data, impots_data = load_data()
    salaire_net = calculer_salaire_net(salaire_brut, age, situation_familiale, lpp_data, impots_data)
    st.success(f"Votre salaire net estimé est de : {salaire_net:.2f} CHF")
