import sys
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).parent))

from src.core.history_manager import HistoryManager
from src.core.interaction_detector import InteractionDetector
from src.core.report_generator import ReportGenerator
from src.database.db_manager import DatabaseManager

st.set_page_config(
    page_title='SafeRx - Assistant Pharmacien Intelligent',
    page_icon='🩺',
    layout='wide',
    initial_sidebar_state='expanded'
)


@st.cache_resource
def load_components():
    start_time = time.time()
    detector = InteractionDetector()
    history_manager = HistoryManager()
    report_generator = ReportGenerator()
    db = DatabaseManager()
    load_time = time.time() - start_time
    return detector, history_manager, report_generator, db, load_time


detector, history_manager, report_generator, db, load_time = load_components()

with st.sidebar:
    st.markdown('<div style="text-align:center; padding:1rem 0;"><div style="font-size:4rem;">🩺</div><h2 style="color:white; margin:0;">SafeRx</h2><p style="color:rgba(255,255,255,0.7);">v2.0 - Performance</p></div>', unsafe_allow_html=True)
    st.markdown('---')
    st.markdown('<div style="color:white;"><h4 style="color:rgba(255,255,255,0.9);">⚡ Performance</h4></div>', unsafe_allow_html=True)

    perf_stats = history_manager.get_performance_stats()
    col1, col2 = st.columns(2)
    with col1:
        st.metric('⏱️ Chargement', f'{load_time:.2f}s')
    with col2:
        st.metric('📊 Analyses', perf_stats['total_analyses'])

    st.metric('⚡ Temps moyen', f"{perf_stats['avg_response_time']:.2f}s")
    st.markdown('---')

    try:
        cache_stats = detector.engine.embedding_engine.get_performance_metrics()
        st.markdown('<div style="color:white;"><h4 style="color:rgba(255,255,255,0.9);">🧠 Cache NLP</h4></div>', unsafe_allow_html=True)
        st.metric('🎯 Hit Rate', cache_stats['cache_hit_rate'])
        st.metric('💾 Cache Size', cache_stats['persistent_cache_size'])
    except Exception:
        pass

    st.markdown('---')
    st.caption('© 2026 SafeRx - SmartRx')


tab1, tab2, tab3, tab4, tab5 = st.tabs(['🏠 Accueil', '📋 Ordonnance', '📊 Analyse', '📈 Historique', '👤 Patients'])

with tab1:
    st.markdown('<h2 style="color:#1a2a6c;">🏠 Tableau de bord SafeRx</h2><p style="color:#4a5568;">Vue d’ensemble des performances et statistiques</p>', unsafe_allow_html=True)
    stats = history_manager.get_statistiques()
    table_stats = db.get_table_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('📋 Analyses', stats['total_analyses'])
    with col2:
        securisees = stats['par_statut'].get('Sécurisée', 0)
        st.metric('✅ Sécurisées', securisees)
    with col3:
        alertes = stats['par_statut'].get('Alerte', 0)
        st.metric('⚠️ Alertes', alertes)
    with col4:
        st.metric('👥 Patients', table_stats.get('Patient', 0))

    st.markdown('---')
    st.subheader('📈 Évolution des analyses')
    perf_stats = history_manager.get_performance_stats()
    if perf_stats['analyses_par_mois']:
        df = pd.DataFrame({
            'Mois': list(perf_stats['analyses_par_mois'].keys()),
            'Analyses': list(perf_stats['analyses_par_mois'].values())
        })
        fig = px.bar(df, x='Mois', y='Analyses', title='Analyses par mois', color='Analyses', color_continuous_scale='Blues')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('ℹ️ Aucune donnée pour le moment')

with tab4:
    st.markdown('<h2 style="color:#1a2a6c;">📋 Historique des analyses</h2><p style="color:#4a5568;">Consultez l’historique complet avec pagination</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        filtre_statut = st.selectbox('Filtrer par statut', ['Tous', 'Sécurisée', 'Alerte', 'Annulée'], key='filter_status')
    with col2:
        page_size = st.selectbox('Lignes par page', [5, 10, 20, 50], index=1, key='page_size')

    total_analyses = history_manager.get_total_analyses(None if filtre_statut == 'Tous' else filtre_statut)

    if total_analyses > 0:
        total_pages = (total_analyses + page_size - 1) // page_size
        if 'page' not in st.session_state:
            st.session_state.page = 1

        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.button('◀ Previous', disabled=st.session_state.page <= 1):
                st.session_state.page = max(1, st.session_state.page - 1)
                st.rerun()
        with col2:
            page = st.number_input('Page', min_value=1, max_value=total_pages, value=st.session_state.page, key='page_input', label_visibility='collapsed')
            st.session_state.page = page
        with col3:
            if st.button('Next ▶', disabled=st.session_state.page >= total_pages):
                st.session_state.page = min(total_pages, st.session_state.page + 1)
                st.rerun()

        offset = (st.session_state.page - 1) * page_size
        result = history_manager.get_historique_paginated(offset=offset, limit=page_size, statut_filter=None if filtre_statut == 'Tous' else filtre_statut)

        for analyse in result['analyses']:
            with st.expander(f"{analyse['date']} - {analyse['patient']} ({analyse['statut']})"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric('📊 Statut', analyse['statut'])
                with col2:
                    st.metric('⚠️ Alertes', analyse['nb_alertes'])
                with col3:
                    st.metric('🔄 Interactions', analyse['nb_interactions'])
                with col4:
                    st.metric('🤧 Allergies', analyse['nb_allergies'])
                st.write(f"💊 Médicaments : {analyse['medicaments']}")

        st.caption(f"Affichage {offset + 1} à {min(offset + page_size, total_analyses)} sur {total_analyses} analyses")
    else:
        st.info('ℹ️ Aucune analyse enregistrée')
