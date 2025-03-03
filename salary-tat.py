import streamlit as st
import pandas as pd

# Définition des taux fixes
TAXES_FIXES = {
    "AVS": 5.30 / 100,
    "AC": 1.10 / 100,
    "Assurance maternité": 0.032 / 100,
    "AANP": 0.63 / 100,
    "APG": 0.495 / 100
}

# Définition des taux LPP en fonction de l'âge
LPP_COTISATIONS = {
    (25, 34): 4.20 / 100,
    (35, 44): 5.70 / 100,
    (45, 54): 8.70 / 100,
    (55, 65): 10.20 / 100
}

# Fonction pour récupérer le taux d'impôt depuis Excel
def get_taux_impot(df):
    """Récupère le taux d'impôt à la source depuis la base Excel"""
    row = df[df.iloc[:, 0] == "Retenue impôt à la source"]
    if not row.empty:
        return float(row.iloc[0, 1])
    return 0

# Fonction de calcul du salaire net
def calculer_salaire_net(salaire_brut, age, df_impots):
    """Calcule les déductions sociales et le salaire net"""
    
    # Calcul des déductions fixes
    avs = salaire_brut * TAXES_FIXES["AVS"]
    ac = salaire_brut * TAXES_FIXES["AC"]
    maternite = salaire_brut * TAXES_FIXES["Assurance maternité"]
    aanp = salaire_brut * TAXES_FIXES["AANP"]
    apg = salaire_brut * TAXES_FIXES["APG"]

    # Calcul de la cotisation LPP
    cotisation_lpp = next((taux for (min_age, max_age), taux in LPP_COTISATIONS.items() if min_age <= age <= max_age), 0) * salaire_brut

    # Calcul de l'impôt à la source (récupéré du fichier)
    taux_impot_source = get_taux_impot(df_impots)
    impot_source = salaire_brut * taux_impot_source

    # Total des déductions
    total_deductions = avs + ac + maternite + aanp + apg + cotisation_lpp + impot_source

    # Salaire net
    salaire_net = salaire_brut - total_deductions

    return salaire_net, cotisation_lpp, avs, ac, maternite, aanp, apg, impot_source, total_deductions

# Interface Streamlit
st.title("🧾 Calcul du Salaire Net")

# Téléchargement du fichier Excel
fichier_excel = st.file_uploader("📂 Téléchargez le fichier Excel des impôts", type=["xlsx"])

if fichier_excel:
    df_impots = pd.read_excel(fichier_excel)

    # Entrées utilisateur
    salaire_brut = st.number_input("💰 Salaire Brut (CHF)", min_value=0, value=13333, step=500)
    age = st.number_input("🎂 Âge", min_value=18, max_value=70, value=30)

    # Calcul des résultats
    salaire_net, cotisation_lpp, avs, ac, maternite, aanp, apg, impot_source, total_deductions = calculer_salaire_net(salaire_brut, age, df_impots)

    # Affichage des résultats
    st.subheader("📊 Résultat")
    st.write(f"💰 **Salaire brut :** {salaire_brut:.2f} CHF")
    st.write(f"🏦 **Caisse de pension LPP :** -{cotisation_lpp:.2f} CHF")
    st.write(f"📉 **Total déductions sociales :** -{total_deductions:.2f} CHF")
    st.write(f"✅ **Salaire net :** {salaire_net:.2f} CHF")

    # Affichage sous forme de fiche de paie
    st.subheader("📑 Fiche de paie")
    st.write("| **Désignation**                 | **Montant (CHF)** |")
    st.write("|--------------------------------|------------------|")
    st.write(f"| 💰 Salaire Brut                 | {salaire_brut:.2f} |")
    st.write(f"| 🏦 Caisse de pension LPP        | -{cotisation_lpp:.2f} |")
    st.write(f"| 🏛 Retenue AVS                  | -{avs:.2f} |")
    st.write(f"| 🏢 Cotisations AC               | -{ac:.2f} |")
    st.write(f"| 🏥 Assurance maternité          | -{maternite:.2f} |")
    st.write(f"| 🚑 Cotisations AANP             | -{aanp:.2f} |")
    st.write(f"| 🏥 Cotisations APG              | -{apg:.2f} |")
    st.write(f"| 🏛 Retenue impôt à la source    | -{impot_source:.2f} |")
    st.write(f"| 📉 **Total déductions sociales** | -{total_deductions:.2f} |")
    st.write(f"| ✅ **Salaire Net**              | **{salaire_net:.2f}** |")
