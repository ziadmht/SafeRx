# test_embedding_app.py
import streamlit as st
from src.nlp.embedding_engine import EmbeddingEngine

st.set_page_config(
    page_title="SafeRx - Moteur Sémantique",
    page_icon="🧪",
    layout="centered"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    .card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        border-left: 5px solid #0d6efd;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 SafeRx - Moteur Sémantique")
st.write("Explorez la puissance du Traitement du Langage Naturel (NLP) pour lier les molécules et les médicaments.")

# Utilisation de st.cache_resource pour éviter de recharger le modèle à chaque interaction
@st.cache_resource
def load_engine():
    return EmbeddingEngine()

with st.spinner("🔄 Chargement du modèle de NLP (all-MiniLM-L6-v2)..."):
    engine = load_engine()

# Liste des molécules connues
molecules = [
    "Aspirine", "Paracétamol", "Ibuprofène", "Warfarine",
    "Amoxicilline", "Pénicilline", "Diclofénac", "Oméprazole"
]

st.subheader("📦 Base de molécules connues")
st.write(", ".join([f"`{m}`" for m in molecules]))

# Interface utilisateur
text = st.text_input("Entrez un médicament, un synonyme ou une molécule :", placeholder="Ex: Doliprane, Advil, Aspirine...")

if text:
    st.write(f"🔍 **Recherche de similarités sémantiques pour** : `{text}`")
    
    # Seuil abaissé à 0.25 pour s'adapter aux caractéristiques du modèle all-MiniLM-L6-v2 sur des termes français
    results = engine.find_similar(text, molecules, threshold=0.25)

    if results:
        st.success(f"✅ {len(results)} molécules similaires trouvées (seuil >= 0.25) :")
        for mol, sim in results:
            st.markdown(f"""
            <div class="card">
                <strong>{mol}</strong><br/>
                <span style="color: #6c757d; font-size: 0.9em;">Score de similarité cosinus : {sim:.4f}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Aucune molécule suffisamment similaire trouvée dans la base.")
