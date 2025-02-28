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
    impots_data = pd.read_excel(xls, sheet_name="Impôts")
    
    # Nettoyage des données (simplifié)
    lpp_data = lpp_data.dropna(how='all').reset_index(drop=True)
    impots_data = impots_data.dropna(how='all').reset_index(drop=True)
    
    return lpp_data, impots_data

# Fonction pour calculer le salaire net
def calculer_salaire_net(salaire_brut, age, situation_familiale, lpp_data, impots_data):
    # Appliquer les cotisations LPP
    print("Valeurs disponibles pour l'âge dans LPP :", lpp_data.iloc[:, 2].unique())
    print("Valeur sélectionnée :", age)
    matching_rows = lpp_data[lpp_data.iloc[:, 2].astype(str).str.strip() == str(age).strip()]
    if matching_rows.empty:
        raise ValueError(f"Aucune correspondance trouvée pour l'âge : {age}")
    taux_lpp = matching_rows.iloc[0, 3]
    cotisation_lpp = salaire_brut * taux_lpp
    
    # Trouver la colonne des impôts correspondant à la situation familiale
    colonne_impot = impots_data.columns[impots_data.iloc[0] == situation_familiale].values[0]
    impots_row = impots_data[(impots_data.iloc[:, 1] <= salaire_brut) & (impots_data.iloc[:, 2] >= salaire_brut)]
    taux_impot = impots_row[colonne_impot].values[0] if not impots_row.empty else 0
    impot = salaire_brut * (taux_impot / 100)
    
    # Calcul du salaire net
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
