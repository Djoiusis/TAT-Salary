import streamlit as st
import pandas as pd

# Tableau LPP intégré
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

lpp_df = pd.DataFrame(LPP_TABLE, columns=["Catégorie Age LPP", "Age", "Epargne (%)", "Risque (%)", "Total (%)"])

# Fonction pour obtenir le taux LPP
def obtenir_taux_lpp(age):
    taux_lpp = lpp_df.loc[lpp_df["Age"] == age, "Total (%)"]
    return taux_lpp.values[0] / 100 if not taux_lpp.empty else 0

# Fonction pour obtenir le taux IS
def obtenir_taux_is(salaire_brut, statut_marital):
    if "Marié" in statut_marital:
        return 7.67 / 100
    elif "Famille monoparentale" in statut_marital:
        return 8.50 / 100
    else:
        return 10.00 / 100

# Fonction principale de calcul du salaire net
def calculer_salaire_net(salaire_brut, age, statut_marital):
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
    taux_lpp = obtenir_taux_lpp(age)
    cotisation_lpp = salaire_brut * taux_lpp

    # Calcul du taux IS automatique
    taux_is = obtenir_taux_is(salaire_brut, statut_marital)
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

# Entrée utilisateur
salaire_brut = st.number_input("💰 Salaire Brut (CHF)", min_value=0, value=13333)
age = st.number_input("🎂 Âge", min_value=25, max_value=65, value=35)

# Liste déroulante pour choisir la situation familiale
situation_familiale = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", options=[
    "Célibataire sans enfant",
    "Marié et le conjoint ne travaille pas et 0 enfant",
    "Marié et le conjoint ne travaille pas et 1 enfant",
    "Marié et le conjoint ne travaille pas et 2 enfants",
    "Marié et les 2 conjoints travaillent et 0 enfant",
    "Marié et les 2 conjoints travaillent et 1 enfant",
    "Famille monoparentale et 1 enfant",
])

if st.button("🧮 Calculer"):
    salaire_net, taux_is, details = calculer_salaire_net(salaire_brut, age, situation_familiale)

    # Affichage des résultats
    st.write(f"### 💰 Salaire Net : {salaire_net:.2f} CHF")
    st.write(f"### 📊 Taux IS Calculé : {taux_is:.2f} %")
    st.write("### 📋 Détails des Déductions :")
    for key, value in details.items():
        st.write(f"- **{key}** : {value:.2f} CHF")
