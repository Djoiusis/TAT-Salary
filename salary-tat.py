import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# 📌 URL du fichier IS.xlsx sur GitHub
GITHUB_URL_IS = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/IS.xlsx"

# 📌 URL du logo
GITHUB_LOGO_URL = "https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/LOGO-Talent-Access-Technologies-removebg.png"

# 📌 Charger les données Excel depuis GitHub
@st.cache_data
def charger_is_data():
    response = requests.get(GITHUB_URL_IS)
    if response.status_code == 200:
        return pd.read_excel(BytesIO(response.content), engine="openpyxl")
    else:
        st.error("❌ Erreur : Impossible de télécharger le fichier Excel.")
        return None

# 📌 **Ajout du style CSS**
st.markdown(
    f"""
    <style>
        .stApp {{
            background: url("https://raw.githubusercontent.com/Djoiusis/TAT-Salary/main/background.jpg") no-repeat center center fixed;
            background-size: cover;
        }}

        .block {{
            background-color: rgba(0, 0, 0, 0.8);
            padding: 25px;
            border-radius: 15px;
            color: white;
            box-shadow: 0px 0px 15px rgba(255, 255, 255, 0.2);
        }}

        .title {{
            text-align: center;
            font-size: 30px;
            font-weight: bold;
            color: white;
            text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.7);
        }}

        .spacer {{
            margin-top: 40px;
            margin-bottom: 40px;
        }}

        .postuler {{
            text-align: center;
            margin-top: 20px;
        }}

        .modal {{
            position: fixed;
            z-index: 999;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 40%;
            background-color: white;
            padding: 20px;
            box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.5);
            border-radius: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# 📌 **Affichage du Logo Centré**
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="{GITHUB_LOGO_URL}" width="250">
    </div>
    """,
    unsafe_allow_html=True
)

# 📌 **Chargement des données IS.xlsx**
is_df = charger_is_data()
if is_df is None:
    st.stop()

# 📌 **Espacement avant la mise en page**
st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

# 📌 **Mise en page en deux colonnes**
col1, col2 = st.columns(2)

# 🔹 **Colonne 1 : Calcul du Salaire Net**
with col1:
    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.header("💰 Calcul du Salaire Net")

    # **Entrées utilisateur**
    salaire_brut_annuel = st.number_input("💰 Salaire Brut Annuel (CHF)", min_value=0, value=160000)
    age = st.number_input("🎂 Âge", min_value=25, max_value=65, value=35)

    # **Sélection de la situation familiale**
    colonnes_a_exclure = ["Mois Max", "Unnamed: 5", "Unnamed: 6", "INDEX", "Année Min", "Année Max", "Mois Min"]
    colonnes_filtrees = [col for col in is_df.columns if col not in colonnes_a_exclure]
    situation_familiale = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", colonnes_filtrees[4:])

    # **Sélection du statut de résidence**
    nationalite = st.radio("🌍 Statut de résidence", ["🇨🇭 Suisse", "🏷️ Permis C", "🌍 Autre (Imposé à la source)"])
    soumis_is = nationalite == "🌍 Autre (Imposé à la source)"

    st.markdown('</div>', unsafe_allow_html=True)

# 🌟 **Espacement entre les blocs**
st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

# 🔹 **Colonne 2 : Simulation Portage Salarial**
with col2:
    st.markdown('<div class="block">', unsafe_allow_html=True)
    st.header("💼 Simulation Portage Salarial")

    # **Entrées utilisateur pour le portage**
    tjm_client = st.number_input("💰 TJM Client (CHF)", min_value=0, value=800)
    jours_travailles = st.number_input("📅 Jours travaillés par mois", min_value=1, max_value=30, value=20)

    st.markdown('</div>', unsafe_allow_html=True)

# 🌟 **Bouton Postuler (Ouvre la popup)**
st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
if st.button("📄 Postuler"):
    st.session_state["popup_active"] = True

# 🌟 **Popup pour renseigner le CV et le numéro de téléphone**
if "popup_active" in st.session_state and st.session_state["popup_active"]:
    st.markdown('<div class="modal">', unsafe_allow_html=True)
    st.subheader("📩 Envoyer ma candidature")

    # 📂 Upload du CV dans la popup
    cv = st.file_uploader("📂 Importer votre CV (PDF uniquement)", type=["pdf"])
    
    # 📞 Champ de numéro de téléphone
    telephone = st.text_input("📞 Numéro de téléphone", placeholder="Ex : +41 79 123 45 67")

    # ✅ Bouton d'envoi
    if st.button("📩 Confirmer ma candidature"):
        if cv is not None and telephone:
            st.success("✅ Candidature envoyée avec succès ! Nous vous contacterons bientôt.")
            st.session_state["popup_active"] = False  # Fermer la popup
        else:
            st.warning("⚠️ Veuillez remplir tous les champs.")

    # ❌ Bouton de fermeture
    if st.button("❌ Annuler"):
        st.session_state["popup_active"] = False  # Fermer la popup

    st.markdown('</div>', unsafe_allow_html=True)
