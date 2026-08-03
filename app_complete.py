import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Ajouter le dossier src au path
sys.path.append(str(Path(__file__).parent))

from src.core.interaction_detector import InteractionDetector
from src.core.history_manager import HistoryManager
from src.core.report_generator import ReportGenerator
from src.database.db_manager import DatabaseManager
from src.nlp.optimized_semantic_engine import OptimizedSemanticEngine

# Garantir l'utilisation explicite du moteur optimisé dans l'application
import src.nlp.optimized_semantic_engine as optimized_module
OptimizedSemanticEngine = optimized_module.OptimizedSemanticEngine

# ============ CONFIGURATION ============
st.set_page_config(
    page_title="SafeRx - Assistant Pharmacien",
    page_icon="🩺",
    layout="wide"
)

st.markdown("""
<style>
html, body, .stApp {
    background: linear-gradient(135deg, #f7fbff 0%, #eef5f8 100%);
    color: #14213d;
}
.main {
    padding-top: 0.4rem;
}
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, rgba(20,33,61,0.98) 0%, rgba(12,26,49,0.98) 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(18px);
}
[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.8);
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    border: 1px solid rgba(148,163,184,0.22);
    backdrop-filter: blur(10px);
}
.stButton > button {
    border-radius: 12px;
    padding: 0.58rem 0.98rem;
    font-weight: 700;
    background: linear-gradient(135deg, #2c6e8f 0%, #3f7fbf 100%);
    color: white;
    border: none;
    box-shadow: 0 8px 18px rgba(63,127,191,0.18);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #245b73 0%, #356a9d 100%);
}
.stTabs [role="tablist"] {
    gap: 0.3rem;
    background: rgba(255,255,255,0.7);
    padding: 0.28rem;
    border-radius: 14px;
    border: 1px solid rgba(148,163,184,0.24);
    box-shadow: 0 6px 14px rgba(15, 23, 42, 0.04);
    backdrop-filter: blur(10px);
}
.stTabs [role="tab"] {
    border-radius: 10px;
    padding: 0.44rem 0.8rem;
    font-weight: 700;
    color: #334155;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2c6e8f 0%, #3f7fbf 100%);
    color: white !important;
}
.block-container {
    padding-top: 0.8rem;
    padding-bottom: 2rem;
}
.hero {
    background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(242,247,251,0.92) 100%);
    border: 1px solid rgba(148,163,184,0.24);
    border-radius: 20px;
    padding: 1.2rem 1.3rem;
    color: #14213d;
    box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);
    margin-bottom: 1rem;
    backdrop-filter: blur(14px);
}
.hero h1 {
    font-size: 1.9rem;
    margin-bottom: 0.2rem;
    color: #14213d;
}
.hero .sub {
    color: #475569;
    font-size: 0.95rem;
}
.card {
    background: rgba(255,255,255,0.82);
    border-radius: 16px;
    padding: 0.95rem 1rem;
    border: 1px solid rgba(148,163,184,0.22);
    box-shadow: 0 10px 22px rgba(15, 23, 42, 0.05);
    backdrop-filter: blur(12px);
}
.card h3, .card h4, .card p, .card label, .card div {
    color: #14213d !important;
}
.badge {
    display: inline-block;
    padding: 0.25rem 0.6rem;
    border-radius: 999px;
    background: #eaf4fb;
    color: #2c6e8f;
    font-size: 0.78rem;
    font-weight: 700;
    margin-right: 0.35rem;
}
.alert-box {
    padding: 0.85rem 0.95rem;
    border-radius: 12px;
    margin: 0.5rem 0;
    border-left: 4px solid;
}
.alert-critical { background: #fef2f2; border-left-color: #ef4444; }
.alert-warning { background: #fff7ed; border-left-color: #f59e0b; }
.alert-info { background: #eff6ff; border-left-color: #3b82f6; }
.alert-success { background: #f0fdf4; border-left-color: #22c55e; }
</style>
""", unsafe_allow_html=True)

# ============ INITIALISATION ============
@st.cache_resource
def load_detector():
    """Charge le détecteur d'interactions optimisé (mis en cache)"""
    return InteractionDetector(engine_class=OptimizedSemanticEngine)

@st.cache_resource
def load_db():
    return DatabaseManager()


detector = load_detector()
db = load_db()
history_manager = HistoryManager()
report_generator = ReportGenerator()

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
      <div style="width:44px; height:44px; border-radius:14px; background:linear-gradient(135deg, #2c6e8f 0%, #3f7fbf 100%); display:flex; align-items:center; justify-content:center; color:white; font-size:20px;">🩺</div>
      <div>
        <div style="font-weight:800; font-size:1.05rem;">SafeRx</div>
        <div style="font-size:0.82rem; opacity:0.8;">Medical Intelligence</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.write("**Assistant Pharmacien**")
    st.write("Version 1.0 - Prototype")
    st.markdown("---")
    
    patients = db.execute_query("SELECT COUNT(*) FROM Patient")
    medicaments = db.execute_query("SELECT COUNT(*) FROM Medicament")
    interactions = db.execute_query("SELECT COUNT(*) FROM Interaction")
    
    st.metric("👥 Patients", patients[0][0])
    st.metric("💊 Médicaments", medicaments[0][0])
    st.metric("⚠️ Interactions", interactions[0][0])
    
    st.markdown("---")
    st.caption("© 2026 SafeRx - SmartRx")

# ============ TITRE ============
st.markdown("""
<div class="hero">
  <div style="display:flex; align-items:center; gap:12px;">
    <div style="width:52px; height:52px; border-radius:16px; background:linear-gradient(135deg, #2c6e8f 0%, #3f7fbf 100%); display:flex; align-items:center; justify-content:center; color:white; font-size:24px; box-shadow:0 8px 18px rgba(63,127,191,0.18);">🩺</div>
    <div>
      <h1>SafeRx</h1>
      <div class="sub">Assistant intelligent de délivrance pharmaceutique — analyses sécurisées, alertes claires et historique professionnel.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ============ TABS ============
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Nouvelle Ordonnance",
    "📊 Analyse",
    "👤 Patients",
    "📚 Médicaments",
    "📋 Historique",
    "📈 Tableau de bord"
])

# ============================================================
# TAB 1 : NOUVELLE ORDONNANCE
# ============================================================
with tab1:
    st.subheader("📋 Saisie d'une ordonnance")
    
    patients = db.execute_query("SELECT idPatient, nom, prenom FROM Patient")
    medicaments = db.execute_query("SELECT idMedicament, nom FROM Medicament")
    
    patient_options = {f"{p[1]} {p[2]}": p[0] for p in patients}
    selected_patient = st.selectbox("👤 Patient", list(patient_options.keys()))
    
    if selected_patient:
        patient_id = patient_options[selected_patient]
        allergies = detector.engine.get_patient_allergies(patient_id)
        if allergies:
            with st.expander("⚠️ Allergies du patient"):
                for mol_id, nom, type_alle, gravite in allergies:
                    if gravite == "Sévère":
                        st.error(f"🔴 {nom} - {type_alle} ({gravite})")
                    elif gravite == "Moyenne":
                        st.warning(f"🟠 {nom} - {type_alle} ({gravite})")
                    else:
                        st.info(f"🟡 {nom} - {type_alle} ({gravite})")
    
    st.subheader("💊 Médicaments prescrits")
    med_options = {m[1]: m[0] for m in medicaments}
    
    if 'medicaments_selectionnes' not in st.session_state:
        st.session_state.medicaments_selectionnes = []
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        med_selection = st.selectbox(
            "Sélectionner un médicament",
            ["Aucun"] + list(med_options.keys())
        )
    
    with col2:
        if st.button("➕ Ajouter"):
            if med_selection != "Aucun" and med_selection not in st.session_state.medicaments_selectionnes:
                st.session_state.medicaments_selectionnes.append(med_selection)
                st.rerun()
    
    if st.session_state.medicaments_selectionnes:
        st.write("**Médicaments sélectionnés :**")
        for med in st.session_state.medicaments_selectionnes:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"  • {med}")
            with col2:
                if st.button("❌", key=f"remove_{med}"):
                    st.session_state.medicaments_selectionnes.remove(med)
                    st.rerun()
        
        if st.button("🔍 Analyser l'ordonnance", type="primary"):
            if selected_patient:
                med_ids = [med_options[m] for m in st.session_state.medicaments_selectionnes]
                with st.spinner("🔄 Analyse en cours..."):
                    resultat = detector.analyser_ordonnance(patient_id, med_ids)
                st.session_state.resultat = resultat
                history_manager.enregistrer_analyse(patient_id, med_ids, resultat)
                st.rerun()
            else:
                st.warning("⚠️ Veuillez sélectionner un patient")
    else:
        st.info("ℹ️ Ajoutez des médicaments en utilisant le sélecteur ci-dessus")

# ============================================================
# TAB 2 : ANALYSE
# ============================================================
with tab2:
    st.subheader("📊 Résultat de l'analyse")
    
    if 'resultat' in st.session_state and st.session_state.resultat is not None:
        resultat = st.session_state.resultat
        detector.afficher_alertes(resultat)
        
        if st.button("🔄 Nouvelle analyse"):
            st.session_state.medicaments_selectionnes = []
            st.session_state.resultat = None
            st.rerun()
    else:
        st.info("ℹ️ Aucune analyse effectuée. Saisissez une ordonnance dans l'onglet 'Nouvelle Ordonnance'.")

# ============================================================
# TAB 3 : PATIENTS
# ============================================================
with tab3:
    st.subheader("👤 Gestion des patients")
    
    patients = db.execute_query("SELECT idPatient, nom, prenom, dateNaissance, sexe, telephone FROM Patient")
    
    for patient in patients:
        with st.expander(f"👤 {patient[1]} {patient[2]}"):
            st.write(f"**ID :** {patient[0]}")
            st.write(f"**Date de naissance :** {patient[3]}")
            st.write(f"**Sexe :** {patient[4]}")
            st.write(f"**Téléphone :** {patient[5]}")
            
            allergies = detector.engine.get_patient_allergies(patient[0])
            if allergies:
                st.write("**⚠️ Allergies :**")
                for mol_id, nom, type_alle, gravite in allergies:
                    if gravite == "Sévère":
                        st.error(f"  - {nom} ({type_alle}, {gravite})")
                    elif gravite == "Moyenne":
                        st.warning(f"  - {nom} ({type_alle}, {gravite})")
                    else:
                        st.info(f"  - {nom} ({type_alle}, {gravite})")
            else:
                st.success("✅ Aucune allergie connue")

# ============================================================
# TAB 4 : MÉDICAMENTS
# ============================================================
with tab4:
    st.subheader("📚 Gestion des médicaments")
    
    medicaments = db.execute_query("""
        SELECT m.idMedicament, m.nom, m.codeCIS, m.forme, m.dosage, m.prix,
               GROUP_CONCAT(mol.nom) as molecules
        FROM Medicament m
        LEFT JOIN Medicament_Molecule mm ON m.idMedicament = mm.idMedicament
        LEFT JOIN Molecule mol ON mm.idMolecule = mol.idMolecule
        GROUP BY m.idMedicament
    """)
    
    for med in medicaments:
        with st.expander(f"💊 {med[1]}"):
            st.write(f"**ID :** {med[0]}")
            st.write(f"**Code CIS :** {med[2]}")
            st.write(f"**Forme :** {med[3]}")
            st.write(f"**Dosage :** {med[4]}")
            st.write(f"**Prix :** {med[5]} DH")
            st.write(f"**Molécules :** {med[6]}")
            
            if st.button(f"🔍 Alternatives", key=f"alt_{med[0]}"):
                alternatives = detector.engine.get_alternatives(med[0], threshold=0.5)
                st.write("**Alternatives similaires :**")
                for alt_nom, sim in alternatives[:5]:
                    st.write(f"  - {alt_nom} (similarité: {sim:.2%})")

# ============================================================
# TAB 5 : HISTORIQUE
# ============================================================
with tab5:
    st.subheader("📋 Historique des analyses")

    col1, col2 = st.columns([2, 1])
    with col1:
        filtre_statut = st.selectbox("Filtrer par statut", ["Tous", "Sécurisée", "Alerte", "Annulée"])
    with col2:
        limite = st.number_input("Nombre d'analyses", min_value=10, max_value=100, value=30)

    historique = history_manager.get_historique(limite)
    if filtre_statut != "Tous":
        historique = [item for item in historique if item["statut"] == filtre_statut]

    if historique:
        for analyse in historique:
            with st.expander(f"📅 {analyse['date']} - {analyse['patient']} ({analyse['statut']})"):
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("📊 Statut", analyse["statut"])
                with col_b:
                    st.metric("⚠️ Alertes", analyse["nb_alertes"])
                with col_c:
                    st.metric("🔄 Interactions", analyse["nb_interactions"])
                with col_d:
                    st.metric("🤧 Allergies", analyse["nb_allergies"])

                st.write(f"💊 Médicaments : {analyse['medicaments']}")

                if st.button(f"🔍 Voir détails", key=f"details_{analyse['id']}"):
                    st.session_state.details_analyse = history_manager.get_analyse_details(analyse["id"])
                    st.rerun()
    else:
        st.info("ℹ️ Aucune analyse enregistrée")

    if "details_analyse" in st.session_state:
        details = st.session_state.details_analyse
        st.markdown("---")
        st.subheader("📄 Détails de l'analyse")
        st.write(f"**Date :** {details['date']}")
        st.write(f"**Patient :** {details['patient']}")
        st.write(f"**Statut :** {details['statut']}")
        st.write(f"**Médicaments :** {', '.join(details.get('medicaments', []))}")

        if details.get("alertes"):
            for alerte in details["alertes"]:
                if alerte["niveau"] == "Élevé":
                    st.error(f"🔴 {alerte['message']}")
                elif alerte["niveau"] == "Moyen":
                    st.warning(f"🟠 {alerte['message']}")
                else:
                    st.info(f"🟡 {alerte['message']}")

                with st.expander("📝 Détails de l'alerte"):
                    st.write(f"**Description :** {alerte['description']}")
                    st.write(f"**Recommandation :** {alerte['recommandation']}")
                    st.write(f"**Médicaments :** {alerte['medicaments']}")

        if st.button("📥 Exporter le rapport (TXT)"):
            rapport = report_generator.generer_rapport_analyse(details)
            chemin = report_generator.exporter_txt(rapport)
            st.success(f"✅ Rapport exporté : {chemin}")
            with open(chemin, "r", encoding="utf-8") as f:
                st.download_button(
                    label="📥 Télécharger le rapport",
                    data=f.read(),
                    file_name=f"rapport_analyse_{details['id']}.txt",
                    mime="text/plain",
                )

        if st.button("❌ Fermer les détails"):
            del st.session_state.details_analyse
            st.rerun()

# ============================================================
# TAB 6 : TABLEAU DE BORD
# ============================================================
with tab6:
    st.subheader("📊 Tableau de bord")

    stats = history_manager.get_statistiques()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total analyses", stats["total_analyses"])
    with col2:
        securisees = stats["par_statut"].get("Sécurisée", 0)
        st.metric("✅ Sécurisées", securisees)
    with col3:
        alertes = stats["par_statut"].get("Alerte", 0)
        st.metric("⚠️ Alertes", alertes)
    with col4:
        taux_securite = (securisees / max(stats["total_analyses"], 1)) * 100
        st.metric("🎯 Taux sécurité", f"{taux_securite:.1f}%")

    st.subheader("📈 Répartition des analyses")
    statut_data = stats.get("par_statut", {})
    if statut_data:
        chart_data = pd.DataFrame({
            "Statut": list(statut_data.keys()),
            "Nombre": list(statut_data.values()),
        })
        chart_data = chart_data.sort_values("Nombre", ascending=False)
        st.bar_chart(chart_data.set_index("Statut"))
    else:
        st.info("Aucune donnée disponible pour le graphique")

    st.subheader("📋 Détail des alertes")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Par type :**")
        type_data = stats.get("par_type_alerte", {})
        if type_data:
            for type_alerte, count in type_data.items():
                st.write(f"- {type_alerte} : {count}")
        else:
            st.write("Aucune alerte")

    with col2:
        st.write("**Par niveau :**")
        niveau_data = stats.get("par_niveau_alerte", {})
        if niveau_data:
            for niveau, count in niveau_data.items():
                if niveau == "Élevé":
                    st.error(f"- {niveau} : {count}")
                elif niveau == "Moyen":
                    st.warning(f"- {niveau} : {count}")
                else:
                    st.info(f"- {niveau} : {count}")
        else:
            st.write("Aucune alerte")

    if st.button("📥 Exporter le rapport global (TXT)"):
        rapport = report_generator.generer_rapport_global(stats)
        chemin = report_generator.exporter_txt(rapport, "rapport_global.txt")
        st.success(f"✅ Rapport exporté : {chemin}")
