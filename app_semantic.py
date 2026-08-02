import streamlit as st
from pathlib import Path
import sys

# Ajouter le dossier src au path
sys.path.append(str(Path(__file__).parent))

from src.nlp.semantic_engine import SemanticEngine
from src.database.db_manager import DatabaseManager

# ============ CONFIGURATION ============
st.set_page_config(
    page_title="SafeRx - Moteur Sémantique",
    page_icon="🧪",
    layout="wide"
)

# ============ INITIALISATION ============
@st.cache_resource
def load_engine():
    """Charge le moteur sémantique (mis en cache)"""
    return SemanticEngine()

engine = load_engine()

# ============ SIDEBAR ============
with st.sidebar:
    st.header("🧪 SafeRx Semantic Engine")
    st.markdown("---")
    st.write("🔍 Recherche sémantique sur la base de données")
    st.write(f"📊 {len(engine.molecules)} molécules")
    st.write(f"💊 {len(engine.medicaments)} médicaments")
    st.write(f"🔗 {len(engine.interactions)} interactions")

# ============ TITRE ============
st.title("🧪 SafeRx - Moteur de Recherche Sémantique")
st.markdown("---")

# ============ TAB 1 : RECHERCHE ============
tab1, tab2, tab3 = st.tabs(["🔍 Recherche Sémantique", "💊 Interactions", "👤 Patient"])

with tab1:
    st.subheader("🔍 Recherche de molécules similaires")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("Entrez un nom de molécule ou médicament :", placeholder="Ex: Aspirine")
    
    with col2:
        threshold = st.slider("Seuil de similarité", 0.0, 1.0, 0.5, 0.05)
    
    if query:
        with st.spinner("Recherche en cours..."):
            results = engine.get_similar_molecules(query, threshold=threshold)
        
        if results:
            st.success(f"✅ {len(results)} résultats trouvés")
            
            for nom, sim, mol_id in results:
                col1, col2, col3 = st.columns([4, 2, 1])
                with col1:
                    st.write(f"**{nom}**")
                with col2:
                    # Barre de progression pour la similarité (cast numpy types to Python float and clamp)
                    sim_val = min(max(float(sim), 0.0), 1.0)
                    st.progress(sim_val)
                with col3:
                    st.write(f"{sim_val:.2%}")
        else:
            st.warning("⚠️ Aucun résultat trouvé")

with tab2:
    st.subheader("💊 Détection d'interactions")
    
    # Sélection des médicaments
    med_names = [m[1] for m in engine.medicaments]
    
    col1, col2 = st.columns(2)
    
    with col1:
        med1 = st.selectbox("Médicament 1", med_names, key="med1")
    
    with col2:
        med2 = st.selectbox("Médicament 2", med_names, key="med2")
    
    if st.button("🔍 Vérifier les interactions"):
        if med1 == med2:
            st.warning("⚠️ Veuillez sélectionner deux médicaments différents")
        else:
            # Récupérer les IDs
            id1 = engine.medicament_by_name.get(med1.lower())
            id2 = engine.medicament_by_name.get(med2.lower())
            
            if id1 and id2:
                interactions = engine.detect_interactions([id1, id2])
                
                if interactions:
                    st.error("⚠️ Interaction détectée !")
                    for mol1, mol2, niveau, desc, reco in interactions:
                        # Trouver les noms
                        nom1 = nom2 = None
                        for m in engine.molecules:
                            if m[0] == mol1:
                                nom1 = m[1]
                            if m[0] == mol2:
                                nom2 = m[1]
                        
                        # Afficher
                        if niveau == "Élevé":
                            st.warning(f"🔴 **{niveau}** : {nom1} + {nom2}")
                        elif niveau == "Moyen":
                            st.info(f"🟠 **{niveau}** : {nom1} + {nom2}")
                        else:
                            st.info(f"🟡 **{niveau}** : {nom1} + {nom2}")
                        
                        st.write(f"📝 {desc}")
                        st.write(f"💡 Recommandation : {reco}")
                else:
                    st.success("✅ Aucune interaction détectée")

with tab3:
    st.subheader("👤 Profil patient et allergies")
    
    # Charger les patients
    db = DatabaseManager()
    patients = db.execute_query("SELECT idPatient, nom, prenom FROM Patient")
    
    patient_options = {f"{p[1]} {p[2]}": p[0] for p in patients}
    selected = st.selectbox("Sélectionner un patient", list(patient_options.keys()))
    
    if selected:
        patient_id = patient_options[selected]
        
        # Informations du patient
        patient = engine.get_patient_by_id(patient_id)
        if patient:
            st.write(f"**Nom :** {patient[1]} {patient[2]}")
            st.write(f"**Date de naissance :** {patient[3]}")
            st.write(f"**Sexe :** {patient[4]}")
        
        # Allergies
        allergies = engine.get_patient_allergies(patient_id)
        
        if allergies:
            st.warning("⚠️ Allergies détectées :")
            for mol_id, nom, type_alle, gravite in allergies:
                if gravite == "Sévère":
                    st.error(f"🔴 **{nom}** - {type_alle} ({gravite})")
                elif gravite == "Moyenne":
                    st.warning(f"🟠 **{nom}** - {type_alle} ({gravite})")
                else:
                    st.info(f"🟡 **{nom}** - {type_alle} ({gravite})")
        else:
            st.success("✅ Aucune allergie connue")
