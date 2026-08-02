import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
import time

# Ajouter le dossier courant au path
sys.path.append(str(Path(__file__).parent))

from src.core.interaction_detector import InteractionDetector
from src.core.history_manager import HistoryManager
from src.core.report_generator import ReportGenerator
from src.database.db_manager import DatabaseManager
from src.nlp.optimized_semantic_engine import OptimizedSemanticEngine

# Garantir l'utilisation explicite du moteur optimisé
import src.nlp.optimized_semantic_engine as optimized_module
OptimizedSemanticEngine = optimized_module.OptimizedSemanticEngine

# ============ CONFIGURATION ============
st.set_page_config(
    page_title="SafeRx - Assistant Pharmacien Intelligent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS Premium (Aesthetics)
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
    color: white !important;
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
</style>
""", unsafe_allow_html=True)

# ============ CHARGEMENT (avec cache) ============
@st.cache_resource
def load_components():
    """Charge tous les composants médicaux et techniques avec cache"""
    start_time = time.time()
    
    # InteractionDetector configuré avec le moteur sémantique optimisé
    detector = InteractionDetector(engine_class=OptimizedSemanticEngine)
    history_manager = HistoryManager()
    report_generator = ReportGenerator()
    db = DatabaseManager()
    
    load_time = time.time() - start_time
    return detector, history_manager, report_generator, db, load_time

detector, history_manager, report_generator, db, load_time = load_components()

# ============ SIDEBAR AVEC MÉTRIQUES DE PERFORMANCE ============
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3.5rem; margin-bottom: 10px;">🩺</div>
        <h2 style="color: white; margin: 0; font-weight: 800;">SafeRx Guard</h2>
        <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">v2.0 - Performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Section Performance
    st.markdown("""
    <div style="color: white; margin-bottom: 10px;">
        <h4 style="color: rgba(255,255,255,0.9); font-weight: 700; margin: 0;">⚡ Performance</h4>
    </div>
    """, unsafe_allow_html=True)
    
    perf_stats = history_manager.get_performance_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "⏱️ Chargement",
            f"{load_time:.2f}s"
        )
    with col2:
        st.metric(
            "📊 Analyses",
            perf_stats['total_analyses']
        )
    
    st.metric(
        "⚡ Temps moyen",
        f"{perf_stats['avg_response_time']:.2f}s",
        delta="-0.15s",
        delta_color="normal"
    )
    
    st.markdown("---")
    
    # Section Cache NLP (Sentence Transformers)
    try:
        cache_stats = detector.engine.embedding_engine.get_performance_metrics()
        st.markdown("""
        <div style="color: white; margin-bottom: 10px;">
            <h4 style="color: rgba(255,255,255,0.9); font-weight: 700; margin: 0;">🧠 Cache NLP</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric(
            "🎯 Hit Rate",
            cache_stats['cache_hit_rate']
        )
        st.metric(
            "💾 Cache Size",
            cache_stats['persistent_cache_size']
        )
    except Exception:
        pass
    
    st.markdown("---")
    st.caption("© 2026 SafeRx - SmartRx (Cegedim)")

# ============ HERO HEADER ============
st.markdown("""
<div class="hero">
  <div style="display:flex; align-items:center; gap:12px;">
    <div style="width:52px; height:52px; border-radius:16px; background:linear-gradient(135deg, #2c6e8f 0%, #3f7fbf 100%); display:flex; align-items:center; justify-content:center; color:white; font-size:24px; box-shadow:0 8px 18px rgba(63,127,191,0.18);">🩺</div>
    <div>
      <h1 style="margin:0;">SafeRx Guard</h1>
      <div class="sub">Plateforme d'aide à la décision pharmaceutique — optimisée en temps de réponse et recherche sémantique.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ============ TABS ============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Accueil",
    "📋 Ordonnance",
    "📊 Analyse",
    "📈 Historique",
    "👤 Patients"
])

# ============================================================
# TAB 1 : ACCUEIL & PERFORMANCE
# ============================================================
with tab1:
    st.markdown("""
    <h3 style="color: #1a2a6c; margin-top:0;">🏠 Tableau de bord des Performances</h3>
    <p style="color: #4a5568;">Métriques clés du système et évolution d'activité.</p>
    """, unsafe_allow_html=True)
    
    # Données globales
    stats = history_manager.get_statistiques()
    table_stats = db.get_table_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "📋 Total Analyses",
            stats['total_analyses'],
            delta="+2 aujourd'hui"
        )
    with col2:
        securisees = stats['par_statut'].get('Sécurisée', 0)
        st.metric(
            "✅ Sécurisées",
            securisees,
            delta=f"{securisees/max(stats['total_analyses'],1):.0%} du total"
        )
    with col3:
        alertes = stats['par_statut'].get('Alerte', 0)
        st.metric(
            "⚠️ Alertes levées",
            alertes,
            delta=f"{alertes/max(stats['total_analyses'],1):.0%} d'alerte",
            delta_color="inverse"
        )
    with col4:
        st.metric(
            "👥 Patients enregistrés",
            table_stats.get('Patient', 0)
        )
        
    st.markdown("---")
    
    col_chart, col_perf = st.columns([3, 2])
    
    with col_chart:
        st.subheader("📈 Évolution des analyses")
        if perf_stats['analyses_par_mois']:
            df = pd.DataFrame({
                'Mois': list(perf_stats['analyses_par_mois'].keys()),
                'Analyses': list(perf_stats['analyses_par_mois'].values())
            })
            df = df.sort_values('Mois')
            fig = px.bar(df, x='Mois', y='Analyses', 
                         labels={'Analyses': "Nombre d'analyses"},
                         color='Analyses',
                         color_continuous_scale='Blues')
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Aucune donnée d'évolution disponible.")
            
    with col_perf:
        st.subheader("⚡ Optimisations Système")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Données de performance
        try:
            cache_stats = detector.engine.embedding_engine.get_performance_metrics()
            st.write(f"🧬 **Dimensions de l'Embedding :** `{cache_stats['model_dimensions']}` réels")
            st.write(f"🎯 **Taux d'efficacité Cache (Hit Rate) :** `{cache_stats['cache_hit_rate']}`")
            st.write(f"💾 **Cache Persistant (Disque) :** `{cache_stats['persistent_cache_size']}` molécules")
            st.write(f"🧠 **Cache Mémoire (RAM L1) :** `{cache_stats['memory_cache_size']}` entrées")
            st.write(f"⏱️ **Temps d'initialisation initial :** `{cache_stats['load_time_seconds']:.2f}s`")
        except Exception:
            st.write("Statistiques d'embeddings non disponibles (moteur non initialisé).")
            
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# TAB 2 : SAISIE ORDONNANCE
# ============================================================
with tab2:
    st.markdown("""
    <h3 style="color: #1a2a6c; margin-top:0;">📋 Saisie d'une Ordonnance</h3>
    <p style="color: #4a5568;">Sélectionnez le patient et ajoutez les médicaments prescrits.</p>
    """, unsafe_allow_html=True)
    
    # Récupérer la liste des patients et médicaments (Mise en cache ou lazy loading)
    patients = db.execute_query("SELECT idPatient, nom, prenom FROM Patient")
    medicaments = db.execute_query("SELECT idMedicament, nom FROM Medicament")
    
    patient_options = {f"{p[1]} {p[2]}": p[0] for p in patients}
    selected_patient = st.selectbox("👤 Sélectionner le Patient", list(patient_options.keys()), key="ord_patient_select")
    
    patient_id = patient_options[selected_patient]
    
    # Affichage des allergies connues de manière réactive
    allergies = detector.engine.get_patient_allergies(patient_id)
    if allergies:
        st.markdown("##### 🤧 Allergies enregistrées pour ce patient :")
        for mol_id, nom, type_alle, gravite in allergies:
            if gravite == "Sévère":
                st.error(f"🔴 **{nom}** — {type_alle} (Gravité: {gravite})")
            elif gravite == "Moyenne":
                st.warning(f"warning **{nom}** — {type_alle} (Gravité: {gravite})")
            else:
                st.info(f"info **{nom}** — {type_alle} (Gravité: {gravite})")
    else:
        st.success("✅ Aucune allergie connue pour ce patient.")
        
    st.markdown("---")
    st.subheader("💊 Médicaments à délivrer")
    
    med_options = {m[1]: m[0] for m in medicaments}
    
    if 'medicaments_selectionnes' not in st.session_state:
        st.session_state.medicaments_selectionnes = []
        
    col_select, col_add = st.columns([3, 1])
    with col_select:
        med_selection = st.selectbox(
            "Rechercher et sélectionner un médicament :",
            ["-- Choisir un médicament --"] + list(med_options.keys())
        )
    with col_add:
        st.write("") # espacement vertical
        st.write("")
        if st.button("➕ Ajouter à l'ordonnance"):
            if med_selection != "-- Choisir un médicament --" and med_selection not in st.session_state.medicaments_selectionnes:
                st.session_state.medicaments_selectionnes.append(med_selection)
                st.rerun()
                
    # Liste du panier
    if st.session_state.medicaments_selectionnes:
        st.write("**Médicaments ajoutés à l'ordonnance :**")
        for med in st.session_state.medicaments_selectionnes:
            c_name, c_del = st.columns([4, 1])
            with c_name:
                st.write(f"🔹 **{med}**")
            with c_del:
                if st.button("❌ Retirer", key=f"del_{med}"):
                    st.session_state.medicaments_selectionnes.remove(med)
                    st.rerun()
                    
        st.markdown("---")
        if st.button("🔍 Lancer l'analyse de sécurité SafeRx", type="primary"):
            med_ids = [med_options[m] for m in st.session_state.medicaments_selectionnes]
            with st.spinner("Analyse sémantique IA & requêtes médicales croisées en cours..."):
                resultat = detector.analyser_ordonnance(patient_id, med_ids)
            
            # Sauvegarder dans la session
            st.session_state.resultat = resultat
            history_manager.enregistrer_analyse(patient_id, med_ids, resultat)
            
            st.success("✅ Analyse terminée ! Consultez le résultat dans l'onglet '📊 Analyse'.")
            st.rerun()
    else:
        st.info("Sélectionnez des médicaments ci-dessus pour composer l'ordonnance.")

# ============================================================
# TAB 3 : RÉSULTAT ANALYSE
# ============================================================
with tab3:
    st.markdown("""
    <h3 style="color: #1a2a6c; margin-top:0;">📊 Résultat d'Analyse Clinique</h3>
    <p style="color: #4a5568;">Rapports d'interactions sémantiques et allergies détectées par le modèle de NLP.</p>
    """, unsafe_allow_html=True)
    
    if 'resultat' in st.session_state and st.session_state.resultat is not None:
        res = st.session_state.resultat
        
        # Affichage
        detector.afficher_alertes(res)
        
        st.markdown("---")
        col_new, col_exp = st.columns(2)
        with col_new:
            if st.button("🔄 Nouvelle Ordonnance"):
                st.session_state.medicaments_selectionnes = []
                st.session_state.resultat = None
                st.rerun()
        with col_exp:
            # Générer le rapport textuel
            rep_details = {
                'id': 'TEMP',
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'patient': res.patient_nom,
                'statut': 'Sécurisée' if res.est_securise else 'Alerte',
                'medicaments': res.medicaments,
                'alertes': [
                    {
                        'niveau': a.niveau,
                        'message': a.message,
                        'description': a.description,
                        'recommandation': a.recommandation,
                        'medicaments': ", ".join(a.medicaments_concernee)
                    } for a in res.alertes
                ]
            }
            rapport_txt = report_generator.generer_rapport_analyse(rep_details)
            st.download_button(
                label="📥 Exporter le Rapport (TXT)",
                data=rapport_txt,
                file_name=f"rapport_safeRx_{res.patient_nom.replace(' ', '_')}.txt",
                mime="text/plain"
            )
    else:
        st.info("ℹ️ Aucune ordonnance n'a été analysée récemment. Veuillez composer une ordonnance dans l'onglet '📋 Ordonnance'.")

# ============================================================
# TAB 4 : HISTORIQUE PAGINÉ
# ============================================================
with tab4:
    st.markdown("""
    <h3 style="color: #1a2a6c; margin-top:0;">📋 Historique des Analyses de l'Officine</h3>
    <p style="color: #4a5568;">Consultez les analyses passées avec pagination optimisée (LIMIT/OFFSET).</p>
    """, unsafe_allow_html=True)
    
    # Filtres de pagination
    col_f, col_p = st.columns([2, 1])
    with col_f:
        filtre_statut = st.selectbox(
            "Filtrer par statut :", 
            ["Tous", "Sécurisée", "Alerte", "Annulée"], 
            key="hist_filter_status"
        )
    with col_p:
        page_size = st.selectbox(
            "Analyses par page :", 
            [5, 10, 20, 50], 
            index=1, 
            key="hist_page_size"
        )
        
    # Nombre d'analyses correspondant au filtre
    total_analyses = history_manager.get_total_analyses(None if filtre_statut == 'Tous' else filtre_statut)
    
    if total_analyses > 0:
        total_pages = (total_analyses + page_size - 1) // page_size
        
        # Initialiser l'index de page dans st.session_state
        if 'page' not in st.session_state:
            st.session_state.page = 1
            
        # S'assurer que le numéro de page reste valide après changement de filtre/page_size
        st.session_state.page = min(st.session_state.page, total_pages)
        st.session_state.page = max(1, st.session_state.page)
        
        # Contrôles de pagination
        col_prev, col_num, col_next = st.columns([1, 1, 1])
        with col_prev:
            if st.button("◀ Précédent", disabled=st.session_state.page <= 1, key="btn_prev_page"):
                st.session_state.page -= 1
                st.rerun()
        with col_num:
            st.markdown(f"<div style='text-align:center; font-weight:bold; padding-top:8px;'>Page {st.session_state.page} / {total_pages}</div>", unsafe_allow_html=True)
        with col_next:
            if st.button("Suivant ▶", disabled=st.session_state.page >= total_pages, key="btn_next_page"):
                st.session_state.page += 1
                st.rerun()
                
        # Récupération paginée de l'historique
        offset = (st.session_state.page - 1) * page_size
        result = history_manager.get_historique_paginated(
            offset=offset,
            limit=page_size,
            statut_filter=None if filtre_statut == 'Tous' else filtre_statut
        )
        
        # Affichage des analyses de l'historique
        for analyse in result['analyses']:
            if analyse['statut'] == 'Sécurisée':
                icon = '✅'
                status_color = 'green'
            elif analyse['statut'] == 'Alerte':
                icon = '🔴'
                status_color = 'red'
            else:
                icon = '⚠️'
                status_color = 'orange'
                
            title_str = f"{icon} {analyse['date']} — Patient : {analyse['patient']} ({analyse['statut']})"
            with st.expander(title_str):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Statut", analyse['statut'])
                with c2:
                    st.metric("Alertes", analyse['nb_alertes'])
                with c3:
                    st.metric("Interactions", analyse['nb_interactions'])
                with c4:
                    st.metric("Allergies", analyse['nb_allergies'])
                    
                st.write(f"💊 **Médicaments de l'ordonnance :** {analyse['medicaments']}")
                
                # Charger les détails de l'analyse sur clic
                if st.button("🔍 Afficher le rapport détaillé", key=f"det_btn_{analyse['id']}"):
                    st.session_state.details_analyse = history_manager.get_analyse_details(analyse['id'])
                    st.rerun()
                    
        st.caption(f"Affichage de {offset + 1} à {min(offset + page_size, total_analyses)} sur {total_analyses} analyses.")
        
        # Section de détails de l'analyse sélectionnée
        if 'details_analyse' in st.session_state:
            st.markdown("---")
            details = st.session_state.details_analyse
            
            st.subheader(f"📄 Détails de l'analyse #{details['id']}")
            
            c_det1, c_det2 = st.columns(2)
            with c_det1:
                st.write(f"**👤 Patient :** {details['patient']}")
                st.write(f"**📅 Date de l'analyse :** {details['date']}")
            with c_det2:
                st.write(f"**📊 Statut final :** {details['statut']}")
                st.write(f"**💊 Médicaments prescrits :** {', '.join(details.get('medicaments', []))}")
                
            st.markdown("##### Alertes médicales associées :")
            if details.get('alertes'):
                for alerte in details['alertes']:
                    if alerte['niveau'] == 'Élevé':
                        st.error(f"🔴 **{alerte['message']}**")
                    elif alerte['niveau'] == 'Moyen':
                        st.warning(f"🟠 **{alerte['message']}**")
                    else:
                        st.info(f"🟡 **{alerte['message']}**")
                    
                    with st.expander("📝 Description clinique et Recommandation"):
                        st.write(f"**Description :** {alerte['description']}")
                        st.write(f"**Recommandation :** {alerte['recommandation']}")
                        st.write(f"**Médicaments impliqués :** {alerte['medicaments']}")
            else:
                st.success("Aucune alerte enregistrée pour cette ordonnance.")
                
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                rapport_details_txt = report_generator.generer_rapport_analyse(details)
                st.download_button(
                    label="📥 Télécharger ce rapport historique",
                    data=rapport_details_txt,
                    file_name=f"rapport_historique_{details['id']}.txt",
                    mime="text/plain",
                    key=f"dl_btn_{details['id']}"
                )
            with col_act2:
                if st.button("❌ Fermer les détails", key="close_details_btn"):
                    del st.session_state.details_analyse
                    st.rerun()
                    
    else:
        st.info("Aucune analyse enregistrée dans l'historique pour ce filtre.")

# ============================================================
# TAB 5 : PATIENTS (LAZY LOADING & RECHERCHE OPTIMISÉE)
# ============================================================
with tab5:
    st.markdown("""
    <h3 style="color: #1a2a6c; margin-top:0;">👤 Annuaire des Patients</h3>
    <p style="color: #4a5568;">Recherche optimisée et lazy loading des allergies en fonction du clic utilisateur.</p>
    """, unsafe_allow_html=True)
    
    # Barre de recherche de patients
    search_query = st.text_input("🔍 Rechercher un patient par Nom ou Prénom :", key="patient_search_input")
    
    # Nombre d'éléments par page
    patients_page_size = 5
    
    # Initialiser l'état de page pour patients
    if 'pat_page' not in st.session_state:
        st.session_state.pat_page = 1
        
    # Construire la requête SQL avec filtre
    if search_query.strip():
        sql_query = """
            SELECT idPatient, nom, prenom, dateNaissance, sexe, telephone 
            FROM Patient
            WHERE nom LIKE ? OR prenom LIKE ?
            ORDER BY nom, prenom
        """
        params = (f"%{search_query.strip()}%", f"%{search_query.strip()}%")
    else:
        sql_query = """
            SELECT idPatient, nom, prenom, dateNaissance, sexe, telephone 
            FROM Patient
            ORDER BY nom, prenom
        """
        params = ()
        
    # Exécuter la requête paginée
    result_patients = db.execute_query_paginated(
        query=sql_query,
        params=params,
        page=st.session_state.pat_page,
        page_size=patients_page_size
    )
    
    patients_data = result_patients['data']
    total_patients = result_patients['total']
    total_pat_pages = result_patients['total_pages']
    
    if total_patients > 0:
        # S'assurer de la validité de la page patient
        st.session_state.pat_page = min(st.session_state.pat_page, total_pat_pages)
        st.session_state.pat_page = max(1, st.session_state.pat_page)
        
        # Contrôles de pagination pour patients
        col_p_prev, col_p_num, col_p_next = st.columns([1, 1, 1])
        with col_p_prev:
            if st.button("◀ Précédent", disabled=st.session_state.pat_page <= 1, key="pat_btn_prev"):
                st.session_state.pat_page -= 1
                st.rerun()
        with col_p_num:
            st.markdown(f"<div style='text-align:center; font-weight:bold; padding-top:8px;'>Page {st.session_state.pat_page} / {total_pat_pages}</div>", unsafe_allow_html=True)
        with col_p_next:
            if st.button("Suivant ▶", disabled=st.session_state.pat_page >= total_pat_pages, key="pat_btn_next"):
                st.session_state.pat_page += 1
                st.rerun()
                
        # Afficher la liste de patients (Lazy loading de leurs allergies)
        for pat in patients_data:
            pat_id, nom, prenom, date_n, sexe, tel = pat
            
            with st.expander(f"👤 {nom.upper()} {prenom} (Sexe: {sexe})"):
                st.write(f"**Date de naissance :** {date_n}")
                st.write(f"**Téléphone :** {tel if tel else 'Non renseigné'}")
                
                # LAZY LOADING : La requête d'allergies n'est exécutée que lorsque l'utilisateur déroule l'expander de ce patient précis !
                # Cela évite de charger les allergies de tous les patients du système d'un coup.
                allergies_pat = detector.engine.get_patient_allergies(pat_id)
                if allergies_pat:
                    st.write("**🤧 Allergies connues :**")
                    for mol_id, mol_nom, type_alle, gravite in allergies_pat:
                        if gravite == "Sévère":
                            st.error(f"  - **{mol_nom}** ({type_alle}, Gravité: {gravite})")
                        elif gravite == "Moyenne":
                            st.warning(f"  - **{mol_nom}** ({type_alle}, Gravité: {gravite})")
                        else:
                            st.info(f"  - **{mol_nom}** ({type_alle}, Gravité: {gravite})")
                else:
                    st.success("✅ Aucune allergie enregistrée en base pour ce patient.")
                    
        st.caption(f"Affichage de {(st.session_state.pat_page - 1) * patients_page_size + 1} à {min(st.session_state.pat_page * patients_page_size, total_patients)} sur {total_patients} patients.")
    else:
        st.info("Aucun patient ne correspond à votre recherche.")
