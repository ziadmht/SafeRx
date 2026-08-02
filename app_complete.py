# app_complete.py - Version Ultra Parfaite avec Aperçu Image et Design Premium
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys
import time
import io
try:
    import requests
except ImportError:
    requests = None

sys.path.append(str(Path(__file__).parent))

from src.core.interaction_detector import InteractionDetector
from src.core.history_manager import HistoryManager
from src.core.report_generator import ReportGenerator
from src.database.db_manager import DatabaseManager
from src.nlp.optimized_semantic_engine import OptimizedSemanticEngine
from src.auth.auth_manager import AuthManager
from src.core.patient_manager import PatientManager
from src.core.medicament_manager import MedicamentManager
from src.core.molecule_manager import MoleculeManager
from src.core.facture_manager import FactureManager
from src.core.constants import Statut, Niveau


# ============================================================
# HORLOGE NUMERIQUE - VERSION JAVASCRIPT (compatible toutes versions)
# ============================================================
def afficher_horloge():
    """Affiche une horloge numerique avec JavaScript - fonctionne sans st.fragment."""
    import streamlit.components.v1 as components
    
    return components.html("""
    <div style="
        display: flex;
        align-items: center;
        gap: 0.8rem;
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.8));
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 0.3rem 1.2rem 0.3rem 0.9rem;
        border-radius: 50px;
        border: 1px solid rgba(26, 86, 219, 0.15);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
        width: fit-content;
        margin-top: 0.2rem;
        transition: all 0.3s ease;
    ">
        <span style="font-size: 0.9rem; opacity: 0.8;">🕐</span>
        <span id="clock-time" style="
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
            font-weight: 700;
            color: #0a1628;
            background: rgba(255, 255, 255, 0.6);
            padding: 0.05rem 0.8rem;
            border-radius: 8px;
            letter-spacing: 0.8px;
            min-width: 80px;
            text-align: center;
            border: 1px solid rgba(26, 86, 219, 0.08);
        ">00:00:00</span>
        <span style="
            font-size: 0.55rem;
            color: #94a3b8;
            padding: 0.15rem 0.5rem;
            background: rgba(255,255,255,0.4);
            border-radius: 12px;
            font-weight: 500;
            letter-spacing: 0.3px;
        " id="clock-date"></span>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            const h = String(now.getHours()).padStart(2, '0');
            const m = String(now.getMinutes()).padStart(2, '0');
            const s = String(now.getSeconds()).padStart(2, '0');
            
            document.getElementById('clock-time').textContent = h + ':' + m + ':' + s;
            
            const options = { day: '2-digit', month: 'short', year: 'numeric' };
            document.getElementById('clock-date').textContent = 
                now.toLocaleDateString('fr-FR', options).replace(/[.]/g, '');
        }
        updateClock();
        setInterval(updateClock, 1000);
    </script>
    """, height=55)


# ============================================================
# FONCTION D'AFFICHAGE UNIQUE - REUTILISEE PARTOUT
# ============================================================
def afficher_analyse(details: dict, contexte: str = "principal"):
    """Affiche une analyse clinique de maniere uniforme."""
    
    if details.get('statut') == Statut.SECURISEE:
        st.markdown("""
        <div class="clinical-alert success" style="padding:1.2rem;">
            <span class="alert-icon" style="font-size:1.5rem;">✓</span>
            <div class="alert-content">
                <div class="alert-title" style="font-size:1rem; color:#166534;">Delivrance autorisee</div>
                <div class="alert-desc" style="font-size:0.88rem;">Aucune interaction critique detectee.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif details.get('statut') == Statut.ALERTE:
        st.markdown("""
        <div class="clinical-alert critical" style="padding:1.2rem;">
            <span class="alert-icon" style="font-size:1.5rem;">■</span>
            <div class="alert-content">
                <div class="alert-title" style="font-size:1rem; color:#991b1b;">Delivrance a risque</div>
                <div class="alert-desc" style="font-size:0.88rem;">Contre-indications detectees.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        statut_label = Statut.label(details.get('statut', 'Inconnu'))
        st.info(f"Statut : {statut_label}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Patient :** {details.get('patient', 'Inconnu')}")
        st.write(f"**Date :** {details.get('date', 'N/A')}")
    with col2:
        statut_val_label = Statut.label(details.get('statut_validation', 'N/A'))
        st.write(f"**Statut validation :** {statut_val_label}")
        st.write(f"**Medicaments :** {', '.join(details.get('medicaments', []))}")
    
    alertes = details.get('alertes', [])
    if alertes:
        st.markdown("### Alertes cliniques")
        for alerte in alertes:
            niveau = alerte.get('niveau', Niveau.FAIBLE)
            
            if niveau == Niveau.ELEVE:
                st.error(f"■ {alerte.get('message', 'Alerte')}")
            elif niveau == Niveau.MOYEN:
                st.warning(f"■ {alerte.get('message', 'Alerte')}")
            else:
                st.info(f"■ {alerte.get('message', 'Alerte')}")
            
            st.write(f"**Description :** {alerte.get('description', 'N/A')}")
            st.write(f"**Recommandation :** {alerte.get('recommandation', 'N/A')}")
            st.write(f"**Medicaments concernes :** {alerte.get('medicaments', 'N/A')}")
            st.markdown("---")
    else:
        st.success("Aucune alerte enregistree.")
    
    analyse_id = details.get('id', 'unknown')
    report_generator = ReportGenerator()
    rapport_txt = report_generator.generer_rapport_analyse(details)
    st.download_button(
        label="Exporter le rapport (TXT)",
        data=rapport_txt,
        file_name=f"Rapport_analyse_{details.get('patient', 'inconnu').replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=True,
        key=f"download_rapport_{contexte}_{analyse_id}"
    )


def main():
    """Application professionnelle SafeRx - Systeme d'Aide a la Delivrance"""
    
    # ============================================================
    # 0. INITIALISATION DES ETATS DE SESSION
    # ============================================================
    if 'analyse_en_cours' not in st.session_state:
        st.session_state.analyse_en_cours = False
    if 'analyse_terminee' not in st.session_state:
        st.session_state.analyse_terminee = False
    if 'resultat' not in st.session_state:
        st.session_state.resultat = None
    if 'medicaments_selectionnes' not in st.session_state:
        st.session_state.medicaments_selectionnes = []
    if 'page_hist' not in st.session_state:
        st.session_state.page_hist = 1
    if 'page_patients' not in st.session_state:
        st.session_state.page_patients = 1
    if 'details_analyse' not in st.session_state:
        st.session_state.details_analyse = None
    if 'show_add_patient' not in st.session_state:
        st.session_state.show_add_patient = False
    if 'show_add_medicament' not in st.session_state:
        st.session_state.show_add_medicament = False
    if 'show_add_molecule' not in st.session_state:
        st.session_state.show_add_molecule = False
    if 'analyse_id_affichee' not in st.session_state:
        st.session_state.analyse_id_affichee = None
    # Ajout pour l'aperçu de l'image scannée
    if 'scan_image_preview' not in st.session_state:
        st.session_state.scan_image_preview = None
    if 'scan_data' not in st.session_state:
        st.session_state.scan_data = None

    # ============================================================
    # 1. AUTHENTIFICATION
    # ============================================================
    auth = AuthManager()
    if not auth.is_authenticated():
        st.warning("Acces restreint - Veuillez vous authentifier.")
        st.stop()

    current_user = auth.get_current_user()
    is_admin = current_user.get('role') == 'Admin'

    import src.nlp.optimized_semantic_engine as optimized_module
    OptimizedSemanticEngine = optimized_module.OptimizedSemanticEngine

    # ============================================================
    # 2. CHARGEMENT DES COMPOSANTS
    # ============================================================
    @st.cache_resource
    def load_components():
        start_time = time.time()
        detector = InteractionDetector(engine_class=OptimizedSemanticEngine)
        history_manager = HistoryManager()
        report_generator = ReportGenerator()
        db = DatabaseManager()
        load_time = time.time() - start_time
        return detector, history_manager, report_generator, db, load_time

    detector, history_manager, report_generator, db, load_time = load_components()

    # ============================================================
    # 3. STYLE CSS ULTRA PREMIUM AVEC APERÇU IMAGE
    # ============================================================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            box-sizing: border-box;
        }
        
        .stApp {
            background: #f5f7fa;
            color: #1a202c;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-12px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .fade-in {
            animation: fadeIn 0.4s ease-out;
        }
        
        .slide-in {
            animation: slideIn 0.3s ease-out;
        }
        
        .main-header {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            padding: 0.6rem 2.5rem;
            margin: -1rem -1rem 1.8rem -1rem;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.04);
            border-bottom: 2px solid #e2e8f0;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .header-logo {
            width: 44px;
            height: 44px;
            background: linear-gradient(135deg, #1a56db, #1e40af);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            color: #ffffff;
            box-shadow: 0 4px 16px rgba(26, 86, 219, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .header-logo:hover {
            transform: scale(1.04) rotate(-2deg);
            box-shadow: 0 6px 24px rgba(26, 86, 219, 0.3);
        }
        
        .header-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #0a1628;
            letter-spacing: -0.3px;
        }
        
        .header-title span {
            color: #1a56db;
        }
        
        .header-subtitle {
            color: #64748b;
            font-size: 0.65rem;
            font-weight: 400;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 1.2rem;
            flex-wrap: wrap;
        }
        
        .header-badge {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            flex-wrap: wrap;
            background: #ffffff;
            padding: 0.2rem 0.8rem 0.2rem 0.5rem;
            border-radius: 30px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 4px rgba(0,0,0,0.02);
        }
        
        .header-badge-item {
            padding: 0.15rem 0.6rem;
            border-radius: 16px;
            color: #475569;
            font-size: 0.6rem;
            font-weight: 500;
            white-space: nowrap;
        }
        
        .header-badge-item.status {
            background: #dcfce7;
            color: #166534;
        }
        
        .header-badge-item.date {
            background: #eff6ff;
            color: #1a56db;
        }
        
        .header-badge-item.version {
            background: linear-gradient(135deg, #1a56db, #60a5fa);
            color: #ffffff;
        }
        
        .header-badge-item strong {
            font-weight: 600;
        }
        
        .status-dot {
            display: inline-block;
            width: 6px;
            height: 6px;
            background: #22c55e;
            border-radius: 50%;
            margin-right: 0.3rem;
            animation: pulse 2s infinite;
        }
        
        .medical-banner {
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            border-radius: 14px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 6px rgba(0, 0, 0, 0.02);
            transition: all 0.3s ease;
        }
        
        .medical-banner:hover {
            border-color: #bfdbfe;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }
        
        .medical-banner h2 {
            font-size: 1.3rem;
            font-weight: 600;
            color: #0a1628;
            margin: 0;
        }
        
        .medical-banner p {
            color: #64748b;
            font-size: 0.85rem;
            margin: 0.3rem 0 0 0;
        }
        
        .banner-stats {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 0.6rem;
        }
        
        .banner-stat {
            text-align: center;
            padding: 0.2rem 0.5rem;
        }
        
        .banner-stat-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: #1a56db;
        }
        
        .banner-stat-label {
            font-size: 0.55rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .stat-card {
            background: #ffffff;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            cursor: default;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #1a56db, #60a5fa);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.4s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            border-color: #bfdbfe;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
        }
        
        .stat-card:hover::after {
            transform: scaleX(1);
        }
        
        .stat-card .stat-icon {
            font-size: 1.2rem;
            margin-bottom: 0.2rem;
            color: #64748b;
        }
        
        .stat-card .stat-number {
            font-size: 1.5rem;
            font-weight: 700;
            color: #0a1628;
            line-height: 1.2;
        }
        
        .stat-card .stat-label {
            font-size: 0.7rem;
            color: #94a3b8;
            font-weight: 500;
            margin-top: 0.1rem;
        }
        
        .stat-card .stat-trend {
            font-size: 0.6rem;
            padding: 0.05rem 0.6rem;
            border-radius: 12px;
            display: inline-block;
            margin-top: 0.2rem;
            font-weight: 600;
        }
        
        .stat-trend.up {
            background: #dcfce7;
            color: #166534;
        }
        
        .stat-trend.down {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .section-card {
            background: #ffffff;
            border-radius: 14px;
            padding: 1.5rem;
            margin: 0.8rem 0;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }
        
        .section-card:hover {
            border-color: #bfdbfe;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }
        
        .section-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #0a1628;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .clinical-alert {
            padding: 0.8rem 1.2rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid;
            display: flex;
            align-items: flex-start;
            gap: 0.8rem;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left-width: 4px;
            transition: all 0.3s ease;
        }
        
        .clinical-alert:hover {
            transform: scale(1.005);
        }
        
        .clinical-alert.critical {
            border-left-color: #dc2626;
            background: #fef2f2;
        }
        
        .clinical-alert.warning {
            border-left-color: #f59e0b;
            background: #fffbeb;
        }
        
        .clinical-alert.info {
            border-left-color: #3b82f6;
            background: #eff6ff;
        }
        
        .clinical-alert.success {
            border-left-color: #22c55e;
            background: #f0fdf4;
        }
        
        .clinical-alert .alert-icon {
            font-size: 1.1rem;
            flex-shrink: 0;
        }
        
        .clinical-alert .alert-content {
            flex: 1;
        }
        
        .clinical-alert .alert-title {
            font-weight: 600;
            font-size: 0.85rem;
            color: #0a1628;
        }
        
        .clinical-alert .alert-desc {
            font-size: 0.8rem;
            color: #475569;
            margin-top: 0.1rem;
            line-height: 1.5;
        }
        
        [data-testid="stSidebar"] {
            background: #0a1628 !important;
        }
        
        .sidebar-logo {
            text-align: center;
            padding: 1.2rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }
        
        .sidebar-logo-icon {
            font-size: 2rem;
            display: block;
            color: #ffffff;
        }
        
        .sidebar-logo-text {
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 700;
        }
        
        .sidebar-logo-text span {
            color: #60a5fa;
        }
        
        .sidebar-section {
            padding: 0.8rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }
        
        .sidebar-section-title {
            color: rgba(255, 255, 255, 0.25);
            font-size: 0.55rem;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .sidebar-metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.25rem 0;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .sidebar-metric-label {
            font-size: 0.7rem;
            font-weight: 300;
        }
        
        .sidebar-metric-value {
            font-weight: 600;
            color: #ffffff;
            font-size: 0.75rem;
        }
        
        .sidebar-metric-value.green {
            color: #4ade80;
        }
        
        .sidebar-metric-value.orange {
            color: #fb923c;
        }
        
        .sidebar-metric-value.red {
            color: #f87171;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.2rem;
            background: #ffffff;
            padding: 0.3rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #475569;
            padding: 0.35rem 1rem;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.75rem;
            transition: all 0.25s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: #f1f5f9;
            color: #0a1628;
        }
        
        .stTabs [aria-selected="true"] {
            background: #1a56db !important;
            color: #ffffff !important;
            box-shadow: 0 2px 12px rgba(26, 86, 219, 0.2);
        }
        
        .stButton button {
            background: linear-gradient(135deg, #1a56db, #1e40af);
            color: #ffffff;
            border: none;
            padding: 0.4rem 1.2rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.8rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .stButton button:hover {
            background: linear-gradient(135deg, #1e40af, #1a56db);
            box-shadow: 0 4px 16px rgba(26, 86, 219, 0.25);
            transform: translateY(-1px);
        }
        
        .stButton button:active {
            transform: scale(0.97);
        }
        
        .stTextInput > div > div {
            border-radius: 8px !important;
            border: 1.5px solid #e2e8f0 !important;
            background: #ffffff !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div:focus-within {
            border-color: #1a56db !important;
            box-shadow: 0 0 0 4px rgba(26, 86, 219, 0.06) !important;
        }
        
        .stSelectbox > div > div {
            border-radius: 8px !important;
            border: 1.5px solid #e2e8f0 !important;
            background: #ffffff !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: #0a1628 !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.7rem !important;
            color: #94a3b8 !important;
            font-weight: 500 !important;
        }
        
        .streamlit-expanderHeader {
            font-size: 0.82rem !important;
            font-weight: 500 !important;
            color: #0a1628 !important;
            background: #f8fafc !important;
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
        }
        
        .streamlit-expanderHeader:hover {
            background: #f1f5f9 !important;
            border-color: #bfdbfe !important;
        }
        
        .stPopover {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 14px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06) !important;
        }
        
        .stProgress > div > div {
            background: linear-gradient(90deg, #1a56db, #60a5fa) !important;
            border-radius: 4px !important;
        }
        
        .app-footer {
            text-align: center;
            color: #94a3b8;
            font-size: 0.55rem;
            padding: 1rem 0 0.5rem 0;
            border-top: 1px solid #e2e8f0;
            margin-top: 2rem;
            letter-spacing: 0.5px;
        }
        
        .app-footer .highlight {
            color: #1a56db;
            font-weight: 500;
        }
        
        /* ✅ Style pour l'aperçu de l'image scannée */
        .scan-preview-container {
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem;
            background: #ffffff;
            min-height: 250px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: border-color 0.3s ease;
        }
        
        .scan-preview-container:hover {
            border-color: #1a56db;
        }
        
        .scan-preview-container img {
            max-height: 350px;
            width: auto;
            max-width: 100%;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        }
        
        .scan-preview-placeholder {
            text-align: center;
            color: #94a3b8;
            padding: 2rem 1rem;
        }
        
        .scan-preview-placeholder .icon {
            font-size: 3rem;
            display: block;
            margin-bottom: 0.5rem;
        }
        
        .scan-extracted-data {
            background: #f8fafc;
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin-top: 0.8rem;
            width: 100%;
            border: 1px solid #e2e8f0;
        }
        
        .scan-extracted-data .label {
            font-size: 0.7rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .scan-extracted-data .value {
            font-weight: 600;
            color: #0a1628;
            font-size: 0.85rem;
        }
        
        @media (max-width: 768px) {
            .header-content { flex-direction: column; align-items: flex-start; }
            .header-title { font-size: 1.2rem; }
            .header-right { width: 100%; justify-content: flex-start; flex-wrap: wrap; }
            .header-badge { flex-wrap: wrap; }
            .stat-card .stat-number { font-size: 1.2rem; }
            .medical-banner { padding: 1rem; }
            .stTabs [data-baseweb="tab"] { padding: 0.25rem 0.6rem; font-size: 0.65rem; }
            .main-header { padding: 0.6rem 1rem; }
            .banner-stats { gap: 0.8rem; }
            .header-badge-item { font-size: 0.5rem; padding: 0.1rem 0.5rem; }
            .scan-preview-container img { max-height: 200px; }
        }
        
        @media print {
            .stSidebar { display: none; }
            .main-header { margin: 0; }
            .scan-preview-container { border: none; }
        }
    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # 4. EN-TETE ULTRA PREMIUM AVEC HORLOGE
    # ============================================================
    date_actuelle = datetime.now().strftime("%d %B %Y")

    st.markdown(f"""
    <div class="main-header fade-in">
        <div class="header-content">
            <div class="header-left">
                <div class="header-logo">⚕</div>
                <div>
                    <div class="header-title">Safe<span>Rx</span></div>
                    <div class="header-subtitle">Systeme d'Aide a la Delivrance · Intelligence Clinique</div>
                </div>
            </div>
            <div class="header-right">
                <div class="header-badge">
                    <span class="header-badge-item status"><span class="status-dot"></span> Operationnel</span>
                    <span class="header-badge-item date">📅 {date_actuelle}</span>
                    <span class="header-badge-item version">SmartRx v2.0</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ✅ HORLOGE - Appel direct
    afficher_horloge()

    # ============================================================
    # 5. BANNIERE
    # ============================================================
    st.markdown("""
    <div class="medical-banner slide-in">
        <h2>Securisation des delivrances en temps reel</h2>
        <p>Analyse semantique des interactions medicamenteuses et des contre-indications allergiques</p>
        <div class="banner-stats">
            <div class="banner-stat">
                <div class="banner-stat-value">all-MiniLM</div>
                <div class="banner-stat-label">Modele semantique L6</div>
            </div>
            <div class="banner-stat">
                <div class="banner-stat-value">100%</div>
                <div class="banner-stat-label">Donnees locales · RGPD</div>
            </div>
            <div class="banner-stat">
                <div class="banner-stat-value">&lt; 0.1s</div>
                <div class="banner-stat-label">Temps de reponse L1</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # 6. SIDEBAR
    # ============================================================
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <span class="sidebar-logo-icon">⚕</span>
            <div class="sidebar-logo-text">Safe<span>Rx</span></div>
            <div style="color: rgba(255,255,255,0.15); font-size: 0.5rem; letter-spacing: 2px; margin-top: 0.1rem;">v2.0 · CLINICAL</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">Indicateurs d\'activite</div>', unsafe_allow_html=True)
        
        stats = history_manager.get_statistiques()
        perf_stats = history_manager.get_performance_stats()
        
        securisees = stats['par_statut'].get(Statut.SECURISEE, 0)
        alertes = stats['par_statut'].get(Statut.ALERTE, 0)
        total_analyses = stats['total_analyses']
        
        st.markdown(f"""
        <div class="sidebar-metric">
            <span class="sidebar-metric-label">Analyses totales</span>
            <span class="sidebar-metric-value">{total_analyses}</span>
        </div>
        <div class="sidebar-metric">
            <span class="sidebar-metric-label">Taux de securite</span>
            <span class="sidebar-metric-value green">{(securisees / max(total_analyses, 1) * 100):.0f}%</span>
        </div>
        <div class="sidebar-metric">
            <span class="sidebar-metric-label">Alertes</span>
            <span class="sidebar-metric-value orange">{alertes}</span>
        </div>
        <div class="sidebar-metric">
            <span class="sidebar-metric-label">Chargement</span>
            <span class="sidebar-metric-value green">{load_time:.2f}s</span>
        </div>
        <div class="sidebar-metric">
            <span class="sidebar-metric-label">Temps reponse</span>
            <span class="sidebar-metric-value green">{perf_stats.get('avg_response_time', 0.85):.2f}s</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">Performance NLP</div>', unsafe_allow_html=True)
        
        try:
            cache_stats = detector.engine.embedding_engine.get_performance_metrics()
            st.markdown(f"""
            <div class="sidebar-metric">
                <span class="sidebar-metric-label">Cache hit rate</span>
                <span class="sidebar-metric-value green">{cache_stats.get('cache_hit_rate', '90.0%')}</span>
            </div>
            <div class="sidebar-metric">
                <span class="sidebar-metric-label">Cache disque</span>
                <span class="sidebar-metric-value">{cache_stats.get('persistent_cache_size', 0)}</span>
            </div>
            <div class="sidebar-metric">
                <span class="sidebar-metric-label">Cache memoire</span>
                <span class="sidebar-metric-value">{cache_stats.get('memory_cache_size', 0)}</span>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown(f"""
        <div style="color:#ffffff; padding:0.4rem 0.6rem; background:rgba(255,255,255,0.04); border-radius:8px; margin-bottom:0.5rem; border:1px solid rgba(255,255,255,0.06);">
            <div style="font-size:0.5rem; color:rgba(255,255,255,0.25); text-transform:uppercase; letter-spacing:0.8px;">Session active</div>
            <div style="font-weight:600; font-size:0.8rem; margin-top:0.1rem;">{current_user['prenom']} {current_user['nom']}</div>
            <div style="font-size:0.55rem; color:#60a5fa;">{current_user['role']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Deconnexion", key="logout_btn", use_container_width=True):
            auth.logout()
            st.rerun()
        
        st.markdown("""
        <div style="color:rgba(255,255,255,0.1); font-size:0.45rem; text-align:center; margin-top:0.8rem; letter-spacing:0.5px;">
            SafeRx · SmartRx<br>Optimized NLP Engine
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # FONCTION FACTORISEE : ENVOI A L'API
    # ============================================================
    def _envoyer_scan_api(data: dict):
        """Envoie une ordonnance scannee a l'API SafeRx."""
        if not data.get("nss"):
            st.error("NSS manquant, impossible d'envoyer le scan.")
            return
        
        try:
            with st.spinner("Analyse en cours..."):
                response = requests.post(
                    "http://localhost:8000/analyse",
                    json={
                        "nss": data["nss"],
                        "medicaments": data["medicaments"],
                        "patient": data.get("patient") or None
                    },
                    timeout=30
                )
            if response.status_code == 200:
                resultat = response.json()
                analyse_id = resultat.get("analyse_id")
                
                if analyse_id:
                    st.session_state.analyse_id_affichee = analyse_id
                    st.success(f"Ordonnance analysee (ID: #{analyse_id}). Consultez l'onglet 'Analyse clinique'.")
                    st.rerun()
                else:
                    st.warning("Analyse effectuee mais aucun ID retourne.")
            else:
                st.error(f"Erreur {response.status_code}")
                try:
                    st.json(response.json())
                except:
                    st.text(response.text)
        except requests.exceptions.ConnectionError:
            st.error("Impossible de joindre l'API. Lancez : uvicorn src.api.api_server:app --reload --port 8000")
        except Exception as e:
            st.error(f"Erreur : {e}")

    # ============================================================
    # 7. TABS
    # ============================================================
    if is_admin:
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            "Tableau de bord",
            "Prescription",
            "Analyse clinique",
            "Historique",
            "Patients",
            "Administration",
            "API Test",
            "Validations",
            "Scan Automatique"
        ])
    else:
        tab1, tab2, tab3, tab4, tab5, tab9 = st.tabs([
            "Tableau de bord",
            "Prescription",
            "Analyse clinique",
            "Historique",
            "Patients",
            "Scan Automatique"
        ])

    # ============================================================
    # TAB 1 : TABLEAU DE BORD
    # ============================================================
    with tab1:
        st.markdown("""
        <div style="margin-bottom:1.2rem; animation: fadeIn 0.3s ease-out;">
            <h2 style="font-size:1.2rem; font-weight:600; color:#0a1628;">Tableau de bord clinique</h2>
            <p style="color:#64748b; font-size:0.85rem;">Indicateurs globaux d'activite et performance</p>
        </div>
        """, unsafe_allow_html=True)
        
        table_stats = db.get_table_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">📋</div>
                <div class="stat-number">{stats['total_analyses']}</div>
                <div class="stat-label">Analyses totales</div>
                <span class="stat-trend up">Session active</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            securisees = stats['par_statut'].get(Statut.SECURISEE, 0)
            pct = (securisees / max(stats['total_analyses'], 1)) * 100
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">✓</div>
                <div class="stat-number" style="color:#22c55e;">{pct:.0f}%</div>
                <div class="stat-label">Delivrances securisees</div>
                <span class="stat-trend up">{securisees} ordonnances</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            alertes = stats['par_statut'].get(Statut.ALERTE, 0)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">⚠</div>
                <div class="stat-number" style="color:#f59e0b;">{alertes}</div>
                <div class="stat-label">Alertes bloquees</div>
                <span class="stat-trend down">Risques evites</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            total_patients = table_stats.get('Patient', 0)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">👤</div>
                <div class="stat-number">{total_patients}</div>
                <div class="stat-label">Patients suivis</div>
                <span class="stat-trend up">Base SQLite</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Activite mensuelle")
            if perf_stats['analyses_par_mois']:
                df = pd.DataFrame({
                    'Mois': list(perf_stats['analyses_par_mois'].keys()),
                    'Analyses': list(perf_stats['analyses_par_mois'].values())
                })
                df = df.sort_values('Mois')
                fig = px.bar(df, x='Mois', y='Analyses', 
                            color='Analyses', 
                            color_continuous_scale='Blues',
                            title="Nombre d'analyses par mois")
                fig.update_layout(
                    height=280,
                    margin=dict(l=10, r=10, t=30, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    title_font=dict(size=13, color='#0a1628')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnee d'historique mensuelle enregistree.")
        
        with col2:
            st.subheader("Repartition des statuts")
            if stats['par_statut']:
                fig = px.pie(
                    values=list(stats['par_statut'].values()),
                    names=list(stats['par_statut'].keys()),
                    color=list(stats['par_statut'].keys()),
                    color_discrete_map={
                        Statut.SECURISEE: Statut.COULEURS[Statut.SECURISEE],
                        Statut.ALERTE: Statut.COULEURS[Statut.ALERTE],
                        Statut.ANNULEE: Statut.COULEURS[Statut.ANNULEE],
                    },
                    title="Distribution des analyses"
                )
                fig.update_layout(
                    height=280,
                    margin=dict(l=10, r=10, t=30, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    title_font=dict(size=13, color='#0a1628'),
                    legend=dict(orientation="h", y=-0.1)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnee disponible")
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Evolution des alertes")
            historique = history_manager.get_historique(limit=100)
            if historique:
                df_alertes = pd.DataFrame(historique)
                df_alertes['date'] = pd.to_datetime(df_alertes['date'])
                df_alertes['mois'] = df_alertes['date'].dt.strftime('%Y-%m')
                
                alertes_par_mois = df_alertes.groupby('mois')['nb_alertes'].sum().reset_index()
                alertes_par_mois = alertes_par_mois.sort_values('mois')
                
                if not alertes_par_mois.empty:
                    fig = px.line(alertes_par_mois, x='mois', y='nb_alertes',
                                  title="Evolution du nombre d'alertes",
                                  markers=True)
                    fig.update_layout(
                        height=260,
                        margin=dict(l=10, r=10, t=30, b=10),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        title_font=dict(size=13, color='#0a1628'),
                        xaxis_title="Mois",
                        yaxis_title="Nombre d'alertes"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Aucune donnee d'alerte disponible")
            else:
                st.info("Aucune donnee d'historique disponible")
                
        with col2:
            st.subheader("Innovation clinique")
            st.markdown("""
            <div class="section-card">
                <strong style="font-size:0.9rem; color:#0a1628;">Traitement Automatique du Langage</strong>
                <p style="color:#475569; font-size:0.82rem; line-height:1.6; margin-top:0.5rem;">
                    SafeRx utilise des Sentence Embeddings pour analyser semantiquement les principes actifs.
                </p>
                <div style="display:flex; gap:0.6rem; margin-top:0.8rem; flex-wrap:wrap;">
                    <span style="background:#eff6ff; color:#1a56db; padding:0.2rem 0.7rem; border-radius:12px; font-size:0.7rem;">Similarite cosinus</span>
                    <span style="background:#f0fdf4; color:#166534; padding:0.2rem 0.7rem; border-radius:12px; font-size:0.7rem;">Sentence-Transformers</span>
                    <span style="background:#fef3c7; color:#92400e; padding:0.2rem 0.7rem; border-radius:12px; font-size:0.7rem;">384 dimensions</span>
                </div>
                <div style="margin-top:0.8rem; padding-top:0.8rem; border-top:1px solid #e2e8f0;">
                    <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:#64748b;">
                        <span>Modele : all-MiniLM-L6-v2</span>
                        <span>Temps moyen : &lt; 0.5s</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ============================================================
    # TAB 2 : PRESCRIPTION
    # ============================================================
    with tab2:
        st.markdown("""
        <div style="margin-bottom:1.2rem; animation: fadeIn 0.3s ease-out;">
            <h2 style="font-size:1.2rem; font-weight:600; color:#0a1628;">Saisie d'une ordonnance</h2>
            <p style="color:#64748b; font-size:0.85rem;">Composer l'ordonnance en selectionnant le patient et ses medicaments</p>
        </div>
        """, unsafe_allow_html=True)
        
        patients = db.execute_query("SELECT idPatient, nom, prenom FROM Patient")
        medicaments = db.execute_query("SELECT idMedicament, nom FROM Medicament")
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Selection du patient</div>', unsafe_allow_html=True)
        
        patient_options = {f"{p[1]} {p[2]}": p[0] for p in patients}
        selected_patient = st.selectbox("Choisir le patient :", list(patient_options.keys()), key="patient_select")
        patient_id = patient_options[selected_patient]
        
        allergies = detector.engine.get_patient_allergies(patient_id)
        if allergies:
            st.markdown("**Allergies connues :**")
            for mol_id, nom, type_alle, gravite in allergies:
                if gravite == "Sévère":
                    st.markdown(f'<div class="clinical-alert critical"><span class="alert-icon">■</span><div class="alert-content"><div class="alert-title">{nom}</div><div class="alert-desc">{type_alle} · Gravite: {gravite}</div></div></div>', unsafe_allow_html=True)
                elif gravite == "Moyenne":
                    st.markdown(f'<div class="clinical-alert warning"><span class="alert-icon">■</span><div class="alert-content"><div class="alert-title">{nom}</div><div class="alert-desc">{type_alle} · Gravite: {gravite}</div></div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="clinical-alert info"><span class="alert-icon">■</span><div class="alert-content"><div class="alert-title">{nom}</div><div class="alert-desc">{type_alle} · Gravite: {gravite}</div></div></div>', unsafe_allow_html=True)
        else:
            st.success("Aucune allergie connue pour ce patient.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Selection des medicaments</div>', unsafe_allow_html=True)
        
        med_options = {m[1]: m[0] for m in medicaments}
        
        col_a, col_b = st.columns([3, 1])
        with col_a:
            med_selection = st.selectbox(
                "Rechercher un medicament :",
                ["-- Selectionner --"] + list(med_options.keys()),
                key="med_select"
            )
        with col_b:
            st.write("")
            st.write("")
            if st.button("Ajouter", key="add_med_btn", use_container_width=True):
                if med_selection != "-- Selectionner --" and med_selection not in st.session_state.medicaments_selectionnes:
                    st.session_state.medicaments_selectionnes.append(med_selection)
                    
        if st.session_state.medicaments_selectionnes:
            st.write("**Medicaments dans l'ordonnance :**")
            for med in st.session_state.medicaments_selectionnes:
                col_med_name, col_med_btn = st.columns([4, 1])
                with col_med_name:
                    st.write(f"• {med}")
                with col_med_btn:
                    if st.button("Retirer", key=f"remove_{med}"):
                        st.session_state.medicaments_selectionnes.remove(med)
                        
            st.markdown("---")
            
            if st.button("Analyser la prescription", key="analyse_btn", type="primary", use_container_width=True):
                if not st.session_state.analyse_en_cours:
                    st.session_state.analyse_en_cours = True
                    try:
                        med_ids = [med_options[m] for m in st.session_state.medicaments_selectionnes]
                        with st.spinner("Analyse semantique en cours..."):
                            resultat = detector.analyser_ordonnance(patient_id, med_ids)
                        
                        analyse_id = history_manager.enregistrer_analyse(patient_id, med_ids, resultat)
                        st.session_state.analyse_id_affichee = analyse_id
                        
                        st.success("Analyse effectuee. Consultez l'onglet 'Analyse clinique'.")
                    except Exception as e:
                        st.error(f"Erreur lors de l'analyse : {e}")
                        import traceback
                        st.code(traceback.format_exc())
                    finally:
                        st.session_state.analyse_en_cours = False
        else:
            st.info("Ajoutez au moins un medicament a l'ordonnance.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # TAB 3 : ANALYSE CLINIQUE
    # ============================================================
    with tab3:
        st.markdown("""
        <div style="margin-bottom:1.2rem; animation: fadeIn 0.3s ease-out;">
            <h2 style="font-size:1.2rem; font-weight:600; color:#0a1628;">Analyse clinique</h2>
            <p style="color:#64748b; font-size:0.85rem;">Resultat de l'analyse semantique de l'ordonnance</p>
        </div>
        """, unsafe_allow_html=True)
        
        analyse_id = st.session_state.get('analyse_id_affichee')
        
        if analyse_id is None:
            st.info("Aucune analyse selectionnee. Effectuez une analyse (Prescription ou Scan) ou choisissez-en une dans l'Historique.")
        else:
            details = history_manager.get_analyse_details(analyse_id)
            if not details:
                st.error("Cette analyse n'existe plus dans la base de donnees.")
            else:
                afficher_analyse(details, contexte="tab3_courant")

    # ============================================================
    # TAB 4 : HISTORIQUE
    # ============================================================
    with tab4:
        st.markdown("""
        <div style="margin-bottom:1.2rem; animation: fadeIn 0.3s ease-out;">
            <h2 style="font-size:1.2rem; font-weight:600; color:#0a1628;">Historique des analyses</h2>
            <p style="color:#64748b; font-size:0.85rem;">Traçabilite complete avec pagination et filtrage</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_filter, col_size = st.columns([2, 1])
        with col_filter:
            filtre_options = ["Tous", Statut.label(Statut.SECURISEE), Statut.label(Statut.ALERTE), Statut.label(Statut.ANNULEE)]
            filtre_statut = st.selectbox(
                "Filtrer par statut :",
                filtre_options,
                key="hist_perf_status"
            )
        with col_size:
            page_size = st.selectbox(
                "Lignes par page :",
                [5, 10, 20, 50],
                index=1,
                key="hist_perf_size"
            )
        
        statut_filter = None if filtre_statut == 'Tous' else {
            Statut.label(Statut.SECURISEE): Statut.SECURISEE,
            Statut.label(Statut.ALERTE): Statut.ALERTE,
            Statut.label(Statut.ANNULEE): Statut.ANNULEE,
        }.get(filtre_statut)
        
        total_analyses = history_manager.get_total_analyses(statut_filter)
        
        if total_analyses > 0:
            total_pages = (total_analyses + page_size - 1) // page_size
            
            st.session_state.page_hist = min(st.session_state.page_hist, total_pages)
            st.session_state.page_hist = max(1, st.session_state.page_hist)
            
            col_p_prev, col_p_num, col_p_next = st.columns([1, 1, 1])
            with col_p_prev:
                if st.button("Precedent", key="hist_prev_btn", disabled=st.session_state.page_hist <= 1):
                    st.session_state.page_hist -= 1
            with col_p_num:
                st.markdown(f"<div style='text-align:center; font-weight:500; font-size:0.85rem; color:#64748b;'>Page {st.session_state.page_hist} / {total_pages}</div>", unsafe_allow_html=True)
            with col_p_next:
                if st.button("Suivant", key="hist_next_btn", disabled=st.session_state.page_hist >= total_pages):
                    st.session_state.page_hist += 1
                    
            offset = (st.session_state.page_hist - 1) * page_size
            result = history_manager.get_historique_paginated(
                offset=offset,
                limit=page_size,
                statut_filter=statut_filter
            )
            
            for analyse in result['analyses']:
                if analyse['statut'] == Statut.SECURISEE:
                    bg_color = '#f0fdf4'
                    border_color = '#22c55e'
                    icon = '✓'
                elif analyse['statut'] == Statut.ALERTE:
                    bg_color = '#fef2f2'
                    border_color = '#dc2626'
                    icon = '■'
                else:
                    bg_color = '#fffbeb'
                    border_color = '#f59e0b'
                    icon = '⚠'
                
                statut_label = Statut.label(analyse['statut'])
                    
                st.markdown(f"""
                <div style="background:{bg_color}; padding:0.8rem 1.2rem; border-radius:10px; border-left:4px solid {border_color}; margin:0.4rem 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                        <div>
                            <strong style="font-size:0.9rem;">{icon} {analyse['date']} — {analyse['patient']}</strong>
                        </div>
                        <div>
                            <span style="background:{border_color}; color:white; padding:0.1rem 0.7rem; border-radius:12px; font-size:0.65rem; font-weight:600;">{statut_label}</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:1.2rem; margin-top:0.3rem; font-size:0.8rem; color:#475569; flex-wrap:wrap;">
                        <span>Alertes : {analyse['nb_alertes']}</span>
                        <span>Medicaments : {analyse['medicaments']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Voir cette analyse", key=f"view_hist_{analyse['id']}"):
                    st.session_state.analyse_id_affichee = analyse['id']
                    st.rerun()
                    
            st.caption(f"Affichage {offset + 1} a {min(offset + page_size, total_analyses)} sur {total_analyses} analyses.")
            
        else:
            st.info("Aucune analyse disponible pour ce filtre.")

    # ============================================================
    # TAB 5 : PATIENTS
    # ============================================================
    with tab5:
        st.markdown("""
        <div style="margin-bottom:1.2rem; animation: fadeIn 0.3s ease-out;">
            <h2 style="font-size:1.2rem; font-weight:600; color:#0a1628;">Gestion des patients</h2>
            <p style="color:#64748b; font-size:0.85rem;">Recherche et consultation des dossiers patients</p>
        </div>
        """, unsafe_allow_html=True)
        
        patient_manager_view = PatientManager()
        
        search_query = st.text_input("Rechercher un patient :", key="patient_perf_search")
        
        patients_page_size = 5
        
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
            
        result_patients = db.execute_query_paginated(
            query=sql_query,
            params=params,
            page=st.session_state.page_patients,
            page_size=patients_page_size
        )
        
        patients_data = result_patients['data']
        total_patients = result_patients['total']
        total_pat_pages = result_patients['total_pages']
        
        if total_patients > 0:
            st.session_state.page_patients = min(st.session_state.page_patients, total_pat_pages)
            st.session_state.page_patients = max(1, st.session_state.page_patients)
            
            col_prev, col_num, col_next = st.columns([1, 1, 1])
            with col_prev:
                if st.button("Precedent", key="pat_prev_btn", disabled=st.session_state.page_patients <= 1):
                    st.session_state.page_patients -= 1
            with col_num:
                st.markdown(f"<div style='text-align:center; font-weight:500; font-size:0.85rem; color:#64748b;'>Page {st.session_state.page_patients} / {total_pat_pages}</div>", unsafe_allow_html=True)
            with col_next:
                if st.button("Suivant", key="pat_next_btn", disabled=st.session_state.page_patients >= total_pat_pages):
                    st.session_state.page_patients += 1
                    
            for patient in patients_data:
                pat_id, nom, prenom, date_n, sexe, tel = patient
                
                with st.expander(f"{nom.upper()} {prenom} ({sexe})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID :** #{pat_id}")
                        st.write(f"**Date de naissance :** {date_n}")
                    with col2:
                        st.write(f"**Telephone :** {tel if tel else 'Non specifie'}")
                        
                    allergies = patient_manager_view.get_allergies(pat_id)
                    if allergies:
                        st.warning("Allergies signalees :")
                        for allergie in allergies:
                            if allergie['gravite'] == "Sévère":
                                st.error(f"  - {allergie['nom']} ({allergie['type']}, Gravite : {allergie['gravite']})")
                            elif allergie['gravite'] == "Moyenne":
                                st.warning(f"  - {allergie['nom']} ({allergie['type']}, Gravite : {allergie['gravite']})")
                            else:
                                st.info(f"  - {allergie['nom']} ({allergie['type']}, Gravite : {allergie['gravite']})")
                    else:
                        st.success("Aucune allergie connue pour ce patient.")
                        
            st.caption(f"Affichage de {(st.session_state.page_patients - 1) * patients_page_size + 1} a {min(st.session_state.page_patients * patients_page_size, total_patients)} sur {total_patients} patients.")
        else:
            st.info("Aucun patient trouve correspondant aux criteres.")

    # ============================================================
    # TAB 6 : ADMINISTRATION (uniquement pour Admin)
    # ============================================================
    if is_admin:
        with tab6:
            st.markdown("""
            <div style="margin-bottom:1.2rem; animation: fadeIn 0.3s ease-out;">
                <h2 style="font-size:1.2rem; font-weight:600; color:#0a1628;">Administration</h2>
                <p style="color:#64748b; font-size:0.85rem;">Gestion complete des donnees cliniques</p>
            </div>
            """, unsafe_allow_html=True)

            sub_patients, sub_medicaments, sub_molecules = st.tabs([
                "Patients",
                "Medicaments",
                "Molecules"
            ])

            with sub_patients:
                patient_manager = PatientManager()
                stats_admin = patient_manager.get_statistics()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total patients", stats_admin['total'])
                with col2:
                    st.metric("Avec allergies", stats_admin['with_allergies'])
                with col3:
                    st.metric("Sans allergies", stats_admin['without_allergies'])
                with col4:
                    st.metric("Taux allergies", f"{stats_admin['with_allergies']/max(stats_admin['total'],1)*100:.0f}%")
                
                st.markdown("---")
                st.subheader("Gestion des patients")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Ajouter un patient", key="add_patient_btn", use_container_width=True):
                        st.session_state.show_add_patient = True
                with col2:
                    if st.button("Rafraichir", key="refresh_patients_btn", use_container_width=True):
                        st.rerun()
                
                if st.session_state.get('show_add_patient', False):
                    with st.expander("Nouveau patient", expanded=True):
                        with st.form("add_patient_form"):
                            col1, col2 = st.columns(2)
                            with col1:
                                nss = st.text_input("NSS", placeholder="123456789012345")
                                nom = st.text_input("Nom *", placeholder="Benjelloun")
                                prenom = st.text_input("Prenom *", placeholder="Karim")
                            with col2:
                                dateNaissance = st.date_input("Date de naissance")
                                sexe = st.selectbox("Sexe", ["M", "F"])
                                telephone = st.text_input("Telephone", placeholder="0612345678")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                submitted = st.form_submit_button("Enregistrer", use_container_width=True)
                            with col2:
                                if st.form_submit_button("Annuler", use_container_width=True):
                                    st.session_state.show_add_patient = False
                                    st.rerun()
                            
                            if submitted:
                                if not nom or not prenom:
                                    st.error("Le nom et le prenom sont obligatoires.")
                                else:
                                    try:
                                        patient_manager.add(
                                            nss=nss or None,
                                            nom=nom,
                                            prenom=prenom,
                                            dateNaissance=dateNaissance.strftime("%Y-%m-%d"),
                                            sexe=sexe,
                                            telephone=telephone or None
                                        )
                                        st.success("Patient ajoute avec succes !")
                                        st.session_state.show_add_patient = False
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erreur : {e}")
                
                patients = patient_manager.get_all()
                molecules = patient_manager.get_molecules()
                
                if patients:
                    st.write(f"**{len(patients)} patients enregistres**")
                    
                    for patient in patients:
                        with st.expander(f"{patient['nom'].upper()} {patient['prenom']} (ID: #{patient['id']})"):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**NSS :** {patient['nss'] or 'Non renseigne'}")
                                st.write(f"**Date de naissance :** {patient['dateNaissance']}")
                                st.write(f"**Sexe :** {patient['sexe']}")
                                st.write(f"**Telephone :** {patient['telephone'] or 'Non renseigne'}")
                            
                            with col2:
                                if st.button("Modifier", key=f"edit_{patient['id']}"):
                                    st.session_state[f"edit_patient_{patient['id']}"] = True
                                if st.button("Supprimer", key=f"delete_{patient['id']}"):
                                    st.session_state[f"delete_patient_{patient['id']}"] = True
                            
                            if st.session_state.get(f"edit_patient_{patient['id']}", False):
                                with st.form(key=f"edit_form_{patient['id']}"):
                                    st.write("**Modifier le patient**")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        edit_nss = st.text_input("NSS", value=patient['nss'] or '', key=f"edit_nss_{patient['id']}")
                                        edit_nom = st.text_input("Nom", value=patient['nom'], key=f"edit_nom_{patient['id']}")
                                        edit_prenom = st.text_input("Prenom", value=patient['prenom'], key=f"edit_prenom_{patient['id']}")
                                    with col2:
                                        edit_date = st.date_input("Date de naissance", value=pd.to_datetime(patient['dateNaissance']), key=f"edit_date_{patient['id']}")
                                        edit_sexe = st.selectbox("Sexe", ["M", "F"], index=0 if patient['sexe'] == 'M' else 1, key=f"edit_sexe_{patient['id']}")
                                        edit_telephone = st.text_input("Telephone", value=patient['telephone'] or '', key=f"edit_tel_{patient['id']}")
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.form_submit_button("Enregistrer", use_container_width=True):
                                            try:
                                                if patient_manager.update(
                                                    patient['id'],
                                                    edit_nss or None,
                                                    edit_nom,
                                                    edit_prenom,
                                                    edit_date.strftime("%Y-%m-%d"),
                                                    edit_sexe,
                                                    edit_telephone or None
                                                ):
                                                    st.success("Patient modifie avec succes !")
                                                    st.session_state[f"edit_patient_{patient['id']}"] = False
                                                    st.rerun()
                                                else:
                                                    st.error("Echec de la modification. Aucune ligne modifiee.")
                                            except Exception as e:
                                                st.error(f"Erreur : {e}")
                                    with col2:
                                        if st.form_submit_button("Annuler", use_container_width=True):
                                            st.session_state[f"edit_patient_{patient['id']}"] = False
                                            st.rerun()
                            
                            if st.session_state.get(f"delete_patient_{patient['id']}", False):
                                st.warning(f"Etes-vous sur de vouloir supprimer {patient['prenom']} {patient['nom']} ?")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Confirmer", key=f"confirm_delete_{patient['id']}"):
                                        try:
                                            if patient_manager.delete(patient['id']):
                                                st.success("Patient supprime avec succes !")
                                                st.session_state[f"delete_patient_{patient['id']}"] = False
                                                st.rerun()
                                            else:
                                                st.error("Echec de la suppression. Le patient a peut-etre des donnees liees.")
                                        except Exception as e:
                                            st.error(f"Erreur : {e}")
                                with col2:
                                    if st.button("Annuler", key=f"cancel_delete_{patient['id']}"):
                                        st.session_state[f"delete_patient_{patient['id']}"] = False
                                        st.rerun()
                            
                            st.markdown("---")
                            st.write("**Allergies**")
                            
                            allergies = patient_manager.get_allergies(patient['id'])
                            
                            if allergies:
                                for allergie in allergies:
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.write(f"• {allergie['nom']} ({allergie['type']}, {allergie['gravite']})")
                                    with col2:
                                        if st.button("✕", key=f"del_allergy_{allergie['id']}"):
                                            patient_manager.delete_allergie(patient['id'], allergie['id'])
                                            st.rerun()
                            else:
                                st.write("_Aucune allergie enregistree_")
                            
                            with st.popover("Ajouter une allergie"):
                                with st.form(key=f"add_allergy_form_{patient['id']}"):
                                    mol_options = {m['nom']: m['id'] for m in molecules}
                                    selected_mol = st.selectbox("Molecule", list(mol_options.keys()), key=f"mol_select_{patient['id']}")
                                    type_alle = st.selectbox("Type", ["Medicament", "Aliment", "Autre"], key=f"type_select_{patient['id']}")
                                    gravite = st.selectbox("Gravite", ["Legere", "Moyenne", "Sévère"], key=f"gravite_select_{patient['id']}")
                                    
                                    if st.form_submit_button("Ajouter l'allergie", use_container_width=True):
                                        try:
                                            if patient_manager.add_allergie(patient['id'], mol_options[selected_mol], type_alle, gravite):
                                                st.success("Allergie ajoutee !")
                                                st.rerun()
                                            else:
                                                st.error("Echec de l'ajout de l'allergie.")
                                        except Exception as e:
                                            st.error(f"Erreur : {e}")
                else:
                    st.info("Aucun patient enregistre.")

            with sub_medicaments:
                medicament_manager = MedicamentManager()
                molecule_manager = MoleculeManager()
                
                stats_med = medicament_manager.get_statistics()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total medicaments", stats_med['total'])
                with col2:
                    st.metric("Avec molecules", stats_med['with_molecules'])
                with col3:
                    st.metric("Sans molecule", stats_med['without_molecules'])
                
                st.markdown("---")
                
                if st.button("Ajouter un medicament", key="add_med_admin_btn", use_container_width=True):
                    st.session_state.show_add_medicament = True
                
                if st.session_state.get('show_add_medicament', False):
                    with st.expander("Nouveau medicament", expanded=True):
                        with st.form("add_medicament_form"):
                            col1, col2 = st.columns(2)
                            with col1:
                                nom = st.text_input("Nom *", placeholder="Aspirine")
                                codeCIS = st.text_input("Code CIS", placeholder="123456")
                                forme = st.text_input("Forme", placeholder="Comprime")
                            with col2:
                                dosage = st.text_input("Dosage", placeholder="500mg")
                                prix = st.number_input("Prix (MAD)", min_value=0.0, step=0.5, format="%.2f")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                submitted = st.form_submit_button("Enregistrer", use_container_width=True)
                            with col2:
                                if st.form_submit_button("Annuler", use_container_width=True):
                                    st.session_state.show_add_medicament = False
                                    st.rerun()
                            
                            if submitted:
                                if not nom:
                                    st.error("Le nom est obligatoire.")
                                else:
                                    ok, msg = medicament_manager.add(nom, codeCIS, forme, dosage, prix)
                                    if ok:
                                        load_components.clear()
                                        st.success(msg)
                                        st.session_state.show_add_medicament = False
                                        st.rerun()
                                    else:
                                        st.error(msg)
                
                medicaments = medicament_manager.get_all()
                all_molecules = {m['nom']: m['id'] for m in molecule_manager.get_all()}
                
                if medicaments:
                    st.write(f"**{len(medicaments)} medicaments enregistres**")
                    
                    for med in medicaments:
                        with st.expander(f"{med['nom']} ({med['codeCIS'] or 'sans code'})"):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**Code CIS :** {med['codeCIS'] or 'Non renseigne'}")
                                st.write(f"**Forme :** {med['forme'] or 'Non renseignee'}")
                                st.write(f"**Dosage :** {med['dosage'] or 'Non renseigne'}")
                                st.write(f"**Prix :** {med['prix']:.2f} MAD")
                            
                            with col2:
                                if st.button("Modifier", key=f"edit_med_{med['id']}"):
                                    st.session_state[f"edit_med_flag_{med['id']}"] = True
                                if st.button("Supprimer", key=f"delete_med_{med['id']}"):
                                    st.session_state[f"delete_med_flag_{med['id']}"] = True
                            
                            if st.session_state.get(f"edit_med_flag_{med['id']}", False):
                                with st.form(key=f"edit_med_form_{med['id']}"):
                                    st.write("**Modifier le medicament**")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        edit_nom = st.text_input("Nom", value=med['nom'], key=f"edit_med_nom_{med['id']}")
                                        edit_codeCIS = st.text_input("Code CIS", value=med['codeCIS'] or '', key=f"edit_med_cis_{med['id']}")
                                        edit_forme = st.text_input("Forme", value=med['forme'] or '', key=f"edit_med_forme_{med['id']}")
                                    with col2:
                                        edit_dosage = st.text_input("Dosage", value=med['dosage'] or '', key=f"edit_med_dosage_{med['id']}")
                                        edit_prix = st.number_input("Prix", value=med['prix'], min_value=0.0, step=0.5, key=f"edit_med_prix_{med['id']}")
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.form_submit_button("Enregistrer", use_container_width=True):
                                            ok, msg = medicament_manager.update(
                                                med['id'], edit_nom, edit_codeCIS, edit_forme, edit_dosage, edit_prix
                                            )
                                            if ok:
                                                load_components.clear()
                                                st.success(msg)
                                                st.session_state[f"edit_med_flag_{med['id']}"] = False
                                                st.rerun()
                                            else:
                                                st.error(msg)
                                    with col2:
                                        if st.form_submit_button("Annuler", use_container_width=True):
                                            st.session_state[f"edit_med_flag_{med['id']}"] = False
                                            st.rerun()
                            
                            if st.session_state.get(f"delete_med_flag_{med['id']}", False):
                                deps = medicament_manager.get_dependencies(med['id'])
                                if deps['has_dependencies']:
                                    st.warning(f"Ce medicament est reference dans {deps['ordonnances']} ordonnance(s) et {deps['analyses']} analyse(s).")
                                else:
                                    st.warning(f"Confirmer la suppression de {med['nom']} ?")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Confirmer", key=f"confirm_del_med_{med['id']}"):
                                        ok, msg = medicament_manager.delete(med['id'])
                                        if ok:
                                            load_components.clear()
                                            st.success(msg)
                                        else:
                                            st.error(msg)
                                        st.session_state[f"delete_med_flag_{med['id']}"] = False
                                        st.rerun()
                                with col2:
                                    if st.button("Annuler", key=f"cancel_del_med_{med['id']}"):
                                        st.session_state[f"delete_med_flag_{med['id']}"] = False
                                        st.rerun()
                            
                            st.markdown("---")
                            st.write("**Molecules associees :**")
                            
                            molecules_associees = medicament_manager.get_molecules(med['id'])
                            
                            if molecules_associees:
                                for mol in molecules_associees:
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.write(f"• {mol['nom']} ({mol['famille'] or 'sans famille'})")
                                    with col2:
                                        if st.button("✕", key=f"unlink_{med['id']}_{mol['id']}"):
                                            ok, msg = medicament_manager.remove_molecule(med['id'], mol['id'])
                                            if ok:
                                                load_components.clear()
                                                st.rerun()
                                            else:
                                                st.error(msg)
                            else:
                                st.write("_Aucune molecule associee_")
                            
                            if all_molecules:
                                with st.popover("Associer une molecule"):
                                    with st.form(key=f"link_mol_form_{med['id']}"):
                                        chosen = st.selectbox("Molecule", list(all_molecules.keys()), key=f"mol_pick_{med['id']}")
                                        if st.form_submit_button("Associer", use_container_width=True):
                                            if all_molecules[chosen] in [m['id'] for m in molecules_associees]:
                                                st.warning("Cette molecule est deja associee.")
                                            else:
                                                ok, msg = medicament_manager.add_molecule(med['id'], all_molecules[chosen])
                                                if ok:
                                                    load_components.clear()
                                                    st.success(msg)
                                                    st.rerun()
                                                else:
                                                    st.error(msg)
                            else:
                                st.info("Aucune molecule disponible. Creez d'abord des molecules.")
                else:
                    st.info("Aucun medicament enregistre.")

            with sub_molecules:
                molecule_manager = MoleculeManager()
                
                stats_mol = molecule_manager.get_statistics()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total molecules", stats_mol['total'])
                with col2:
                    st.metric("Familles", len(stats_mol['familles']))
                
                st.markdown("---")
                
                if st.button("Ajouter une molecule", key="add_mol_admin_btn", use_container_width=True):
                    st.session_state.show_add_molecule = True
                
                if st.session_state.get('show_add_molecule', False):
                    with st.expander("Nouvelle molecule", expanded=True):
                        with st.form("add_molecule_form"):
                            col1, col2 = st.columns(2)
                            with col1:
                                nom = st.text_input("Nom *", placeholder="Acide acetylsalicylique")
                                famille = st.text_input("Famille", placeholder="AINS")
                            with col2:
                                formule = st.text_input("Formule chimique", placeholder="C9H8O4")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                submitted = st.form_submit_button("Enregistrer", use_container_width=True)
                            with col2:
                                if st.form_submit_button("Annuler", use_container_width=True):
                                    st.session_state.show_add_molecule = False
                                    st.rerun()
                            
                            if submitted:
                                if not nom:
                                    st.error("Le nom est obligatoire.")
                                else:
                                    ok, msg = molecule_manager.add(nom, famille, formule)
                                    if ok:
                                        load_components.clear()
                                        st.success(msg)
                                        st.session_state.show_add_molecule = False
                                        st.rerun()
                                    else:
                                        st.error(msg)
                
                molecules = molecule_manager.get_all()
                
                if molecules:
                    st.write(f"**{len(molecules)} molecules enregistrees**")
                    
                    for mol in molecules:
                        with st.expander(f"{mol['nom']} ({mol['famille'] or 'sans famille'})"):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**Famille :** {mol['famille'] or 'Non renseignee'}")
                                st.write(f"**Formule :** {mol['formule'] or 'Non renseignee'}")
                            
                            with col2:
                                if st.button("Modifier", key=f"edit_mol_{mol['id']}"):
                                    st.session_state[f"edit_mol_flag_{mol['id']}"] = True
                                if st.button("Supprimer", key=f"delete_mol_{mol['id']}"):
                                    st.session_state[f"delete_mol_flag_{mol['id']}"] = True
                            
                            if st.session_state.get(f"edit_mol_flag_{mol['id']}", False):
                                with st.form(key=f"edit_mol_form_{mol['id']}"):
                                    st.write("**Modifier la molecule**")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        edit_nom = st.text_input("Nom", value=mol['nom'], key=f"edit_mol_nom_{mol['id']}")
                                        edit_famille = st.text_input("Famille", value=mol['famille'] or '', key=f"edit_mol_famille_{mol['id']}")
                                    with col2:
                                        edit_formule = st.text_input("Formule", value=mol['formule'] or '', key=f"edit_mol_formule_{mol['id']}")
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.form_submit_button("Enregistrer", use_container_width=True):
                                            ok, msg = molecule_manager.update(mol['id'], edit_nom, edit_famille, edit_formule)
                                            if ok:
                                                load_components.clear()
                                                st.success(msg)
                                                st.session_state[f"edit_mol_flag_{mol['id']}"] = False
                                                st.rerun()
                                            else:
                                                st.error(msg)
                                    with col2:
                                        if st.form_submit_button("Annuler", use_container_width=True):
                                            st.session_state[f"edit_mol_flag_{mol['id']}"] = False
                                            st.rerun()
                            
                            if st.session_state.get(f"delete_mol_flag_{mol['id']}", False):
                                deps = molecule_manager.get_dependencies(mol['id'])
                                if deps['has_dependencies']:
                                    st.warning(
                                        f"Cette molecule est utilisee dans :\n"
                                        f"- {deps['medicaments']} medicament(s)\n"
                                        f"- {deps['interactions']} interaction(s)\n"
                                        f"- {deps['allergies']} allergie(s)\n"
                                        f"Retirez d'abord ces associations."
                                    )
                                else:
                                    st.warning(f"Confirmer la suppression de {mol['nom']} ?")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if deps['has_dependencies']:
                                        st.button("Confirmer", disabled=True, key=f"confirm_del_mol_{mol['id']}")
                                    else:
                                        if st.button("Confirmer", key=f"confirm_del_mol_{mol['id']}"):
                                            ok, msg = molecule_manager.delete(mol['id'])
                                            if ok:
                                                load_components.clear()
                                                st.success(msg)
                                            else:
                                                st.error(msg)
                                            st.session_state[f"delete_mol_flag_{mol['id']}"] = False
                                            st.rerun()
                                with col2:
                                    if st.button("Annuler", key=f"cancel_del_mol_{mol['id']}"):
                                        st.session_state[f"delete_mol_flag_{mol['id']}"] = False
                                        st.rerun()
                else:
                    st.info("Aucune molecule enregistree.")

    # ============================================================
    # TAB 7 : API TEST
    # ============================================================
    if is_admin:
        with tab7:
            st.markdown("""
            <div style="margin-bottom:1.2rem; animation: fadeIn 0.3s ease-out;">
                <h2 style="font-size:1.2rem; font-weight:600; color:#0a1628;">Test de l'API de scanning</h2>
                <p style="color:#64748b; font-size:0.85rem;">Simule l'envoi d'une ordonnance scannee depuis un systeme externe</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("api_test_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Patient**")
                    nss = st.text_input("NSS", value="123456789012345", key="api_nss")
                    nom = st.text_input("Nom", value="Benjelloun", key="api_nom")
                    prenom = st.text_input("Prenom", value="Karim", key="api_prenom")
                    dateNaissance = st.date_input("Date de naissance", key="api_date")
                    sexe = st.selectbox("Sexe", ["M", "F"], key="api_sexe")
                    telephone = st.text_input("Telephone", value="0612345678", key="api_tel")
                
                with col2:
                    st.markdown("**Ordonnance**")
                    medicaments_text = st.text_area(
                        "Medicaments (un par ligne)",
                        value="Aspirine\nCoumadine\nDoliprane",
                        key="api_meds"
                    )
                    medicaments_liste = [m.strip() for m in medicaments_text.split('\n') if m.strip()]
                    
                    st.markdown("**Resume**")
                    st.write(f"Medicaments : {len(medicaments_liste)}")
                    for m in medicaments_liste:
                        st.write(f"  • {m}")
                
                submitted = st.form_submit_button("Envoyer a l'API", type="primary", use_container_width=True)
            
            if submitted:
                if not requests:
                    st.error("La bibliotheque 'requests' n'est pas installee.")
                else:
                    with st.spinner("Analyse en cours..."):
                        try:
                            patient_data = {
                                "nom": nom,
                                "prenom": prenom,
                                "dateNaissance": dateNaissance.strftime("%Y-%m-%d"),
                                "sexe": sexe,
                                "telephone": telephone
                            }
                            
                            response = requests.post(
                                "http://localhost:8000/analyse",
                                json={
                                    "nss": nss,
                                    "medicaments": medicaments_liste,
                                    "patient": patient_data
                                },
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                analyse_id = data.get("analyse_id")
                                
                                st.success("Analyse terminee avec succes !")
                                
                                if analyse_id:
                                    st.session_state.analyse_id_affichee = analyse_id
                                    st.info(f"Analyse #{analyse_id} disponible dans l'onglet 'Analyse clinique'.")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("### Patient")
                                    st.json(data.get('patient', {}))
                                
                                with col2:
                                    st.markdown("### Statut")
                                    st.write(f"**Statut :** {data.get('statut', 'Inconnu')}")
                                    st.write(f"**Alertes :** {data.get('nb_alertes', 0)}")
                                
                                st.markdown("### Medicaments analyses")
                                st.write(", ".join(data.get('medicaments', [])))
                                
                                st.markdown("### Alertes")
                                if data.get('alertes'):
                                    for alerte in data['alertes']:
                                        if alerte['niveau'] == Niveau.ELEVE:
                                            st.error(f"■ {alerte['message']}")
                                        elif alerte['niveau'] == Niveau.MOYEN:
                                            st.warning(f"■ {alerte['message']}")
                                        else:
                                            st.info(f"■ {alerte['message']}")
                                else:
                                    st.success("Aucune alerte")
                                
                                with st.popover("Voir le JSON complet"):
                                    st.json(data)
                                    
                            else:
                                st.error(f"Erreur {response.status_code}")
                                try:
                                    st.json(response.json())
                                except:
                                    st.text(response.text)
                                    
                        except requests.exceptions.ConnectionError:
                            st.error("Impossible de se connecter a l'API. Verifiez que le serveur est lance.")
                            st.code("uvicorn src.api.api_server:app --reload --port 8000")
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                            import traceback
                            st.code(traceback.format_exc())

    # ============================================================
    # TAB 8 : FILE D'ATTENTE DES VALIDATIONS (COMPLETEMENT CORRIGE)
    # ============================================================
    if is_admin:
        with tab8:
            st.markdown("""
            <div style="margin-bottom:1.2rem; animation: fadeIn 0.3s ease-out;">
                <h2 style="font-size:1.2rem; font-weight:600; color:#0a1628;">File d'attente des validations</h2>
                <p style="color:#64748b; font-size:0.85rem;">Ordonnances scannees en attente de validation par le pharmacien</p>
            </div>
            """, unsafe_allow_html=True)
            
            en_attente = db.execute_query("""
                SELECT a.idAnalyse, a.dateAnalyse, p.nom || ' ' || p.prenom as patient_nom, 
                       a.statut, a.nb_alertes, a.nb_interactions, a.nb_allergies,
                       a.statut_validation
                FROM Analyse a
                JOIN Patient p ON a.idPatient = p.idPatient
                WHERE a.statut_validation = 'EN_ATTENTE'
                ORDER BY a.dateAnalyse DESC
            """)
            
            if not en_attente:
                st.info("Aucune ordonnance en attente de validation.")
            else:
                st.write(f"**{len(en_attente)} ordonnance(s) en attente**")
                
                for row in en_attente:
                    analyse_id, date, patient_nom, statut, nb_alertes, nb_interactions, nb_allergies, statut_val = row
                    
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.write(f"**#{analyse_id}** — {patient_nom} — {date}")
                            if nb_alertes > 0:
                                st.warning(f"{nb_alertes} alerte(s) ({nb_interactions} interactions, {nb_allergies} allergies)")
                            else:
                                st.success("Aucune alerte")
                        
                        with col2:
                            if st.button("Valider", key=f"valider_{analyse_id}", use_container_width=True):
                                try:
                                    facture_manager = FactureManager()
                                    
                                    rows_updated = db.execute_write_rowcount(
                                        "UPDATE Analyse SET statut_validation = 'VALIDEE' WHERE idAnalyse = ? AND statut_validation = 'EN_ATTENTE'",
                                        (analyse_id,)
                                    )
                                    
                                    if rows_updated == 0:
                                        st.warning("Cette analyse a deja ete traitee.")
                                    else:
                                        details = history_manager.get_analyse_details(analyse_id)
                                        patient_id = db.execute_query(
                                            "SELECT idPatient FROM Analyse WHERE idAnalyse = ?",
                                            (analyse_id,)
                                        )[0][0]
                                        medicaments = details.get('medicaments', [])
                                        
                                        ok, msg, facture = facture_manager.generer_facture(
                                            analyse_id,
                                            patient_id,
                                            medicaments,
                                            db
                                        )
                                        
                                        if ok:
                                            from src.core.facture_generator import envoyer_a_paiement
                                            paiement = envoyer_a_paiement(facture)
                                            facture_manager.payer(facture['id'], paiement['reference'])
                                            st.success(f"Delivrance validee. Facture {facture['numero']} transmise.")
                                            st.rerun()
                                        else:
                                            st.error(f"Erreur facturation : {msg}")
                                            # ✅ CORRECTION : rollback avec le bon format
                                            db.execute_write(
                                                "UPDATE Analyse SET statut_validation = 'EN_ATTENTE' WHERE idAnalyse = ?",
                                                (analyse_id,)
                                            )
                                except Exception as e:
                                    st.error(f"Erreur : {e}")
                        
                        with col3:
                            if st.button("Annuler", key=f"annuler_{analyse_id}", use_container_width=True):
                                rows_updated = db.execute_write_rowcount(
                                    "UPDATE Analyse SET statut_validation = 'ANNULEE', date_validation = CURRENT_TIMESTAMP WHERE idAnalyse = ? AND statut_validation = 'EN_ATTENTE'",
                                    (analyse_id,)
                                )
                                if rows_updated > 0:
                                    st.info("Ordonnance annulee.")
                                    st.rerun()
                                else:
                                    st.warning("Cette analyse a deja ete traitee.")

    # ============================================================
    # TAB 9 : SCAN AUTOMATIQUE AVEC APERCU IMAGE (CORRIGE)
    # ============================================================
    with tab9:
        st.markdown("""
        <div style="margin-bottom:1.2rem; animation: fadeIn 0.3s ease-out;">
            <h2 style="font-size:1.2rem; font-weight:600; color:#0a1628;">📷 Scan Automatique d'Ordonnance</h2>
            <p style="color:#64748b; font-size:0.85rem;">
                Simulation d'un scanner d'ordonnance connecte a l'API SafeRx. 
                <strong style="color:#dc2626;">Aucune saisie manuelle requise.</strong>
            </p>
            <p style="color:#64748b; font-size:0.8rem; margin-top:0.3rem;">
                📁 Formats supportes : JSON, JPG, PNG, PDF
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        from src.core.scanner_simulator import ScannerSimulator
        scanner = ScannerSimulator()
        
        col1, col2 = st.columns([1, 1])
        
        # ---- Colonne 1 : Upload et données ----
        with col1:
            st.markdown('<div class="section-card"><div class="section-title">📂 Fichier scanne</div>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Telecharger l'ordonnance scannee",
                type=["json", "jpg", "jpeg", "png", "pdf"],
                key="scan_upload",
                help="Formats supportes : JSON, JPG, PNG, PDF"
            )
            
            if uploaded_file is not None:
                # ✅ Capturer les octets bruts UNE SEULE FOIS avant tout traitement
                file_bytes = uploaded_file.getvalue()
                file_type = uploaded_file.type
                file_name = uploaded_file.name
                
                # Stocker les bytes pour l'aperçu (indépendant du curseur)
                st.session_state.scan_image_preview = {
                    "bytes": file_bytes,
                    "type": file_type,
                    "name": file_name,
                }
                
                try:
                    extension = file_name.split('.')[-1].lower()
                    
                    if extension in ['json']:
                        data = scanner.lire_fichier(uploaded_file)
                        st.session_state.scan_data = data
                    else:
                        with st.spinner("🔍 Analyse OCR en cours..."):
                            # ✅ Passer une copie fraîche du flux à l'OCR avec le nom d'origine
                            data = scanner.scanner_image(io.BytesIO(file_bytes), nom_original=file_name)
                            st.session_state.scan_data = data
                            
                            if data.get('nss'):
                                st.info(f"🔍 NSS identifie : {data['nss']}")
                            if data.get('medicaments'):
                                st.info(f"💊 Medicaments identifies : {', '.join(data['medicaments'])}")
                    
                    if data:
                        st.write(f"**NSS :** {data.get('nss', 'Non trouve')}")
                        st.write(f"**Medicaments :** {', '.join(data.get('medicaments', []))}")
                        
                        if st.button("📤 Envoyer a l'API", key="scan_upload_btn", type="primary", use_container_width=True):
                            _envoyer_scan_api(data)
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse : {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ---- Selection manuelle ----
            st.markdown('<div class="section-card"><div class="section-title">👤 Selection patient</div>', unsafe_allow_html=True)
            
            patients = scanner.get_patients()
            nss_options = list(patients.keys())
            labels = [f"{patients[n]['prenom']} {patients[n]['nom']} ({n})" for n in nss_options]
            choix = st.selectbox("Patient :", labels, key="scan_patient_select")
            nss_choisi = nss_options[labels.index(choix)]
            patient_choisi = patients[nss_choisi]
            
            st.write(f"**Patient :** {patient_choisi['prenom']} {patient_choisi['nom']}")
            st.write(f"**NSS :** {nss_choisi}")
            
            st.markdown("---")
            
            st.markdown("**💊 Medicaments presents sur l'ordonnance :**")
            meds_selectionnes = st.multiselect(
                "Selectionner les medicaments :",
                scanner.get_medicaments(),
                key="scan_meds_multiselect",
                placeholder="Choisissez les medicaments..."
            )
            
            if meds_selectionnes:
                st.write(f"**{len(meds_selectionnes)} medicament(s) selectionne(s)**")
                st.write(f"• {', '.join(meds_selectionnes)}")
                
                if st.button("📤 Envoyer a l'API", key="scan_select_btn", type="primary", use_container_width=True):
                    _envoyer_scan_api({
                        "nss": nss_choisi,
                        "medicaments": meds_selectionnes,
                        "patient": patient_choisi
                    })
            else:
                st.info("ℹ️ Selectionnez au moins un medicament.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # ---- Colonne 2 : APERCU DE L'IMAGE SCANNÉE ----
        with col2:
            st.markdown('<div class="section-card"><div class="section-title">🖼️ Ordonnance scannee</div>', unsafe_allow_html=True)
            
            preview = st.session_state.get('scan_image_preview')
            
            if preview is not None:
                try:
                    # Afficher l'aperçu
                    st.markdown('<div class="scan-preview-container">', unsafe_allow_html=True)
                    
                    if preview["type"].startswith('image/'):
                        # ✅ st.image accepte des bytes bruts - compatible toutes versions Streamlit
                        st.image(preview["bytes"], caption="Ordonnance scannée", use_column_width=True)
                    elif preview["type"] == 'application/pdf':
                        st.info("📄 PDF téléchargé")
                        st.write(f"**Fichier :** {preview['name']}")
                        st.write(f"**Taille :** {len(preview['bytes']) / 1024:.1f} KB")
                        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/PDF_file_icon.svg/120px-PDF_file_icon.svg.png", width=80)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Afficher les données extraites si disponibles
                    if st.session_state.get('scan_data'):
                        data = st.session_state.scan_data
                        st.markdown('<div class="scan-extracted-data">', unsafe_allow_html=True)
                        st.markdown('<span class="label">📊 Données extraites</span>', unsafe_allow_html=True)
                        st.write(f"**NSS :** {data.get('nss', 'Non trouvé')}")
                        if data.get('medicaments'):
                            st.write(f"**💊 Médicaments :** {', '.join(data['medicaments'])}")
                        else:
                            st.write("**💊 Médicaments :** Aucun identifié")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        if st.button("🔄 Effacer l'aperçu", key="clear_preview"):
                            st.session_state.scan_image_preview = None
                            st.session_state.scan_data = None
                            st.rerun()
                except Exception as e:
                    st.error(f"Erreur d'affichage : {e}")
                    st.warning("L'image ne peut pas être affichée.")
            else:
                # Placeholder
                st.markdown("""
                <div class="scan-preview-container">
                    <div class="scan-preview-placeholder">
                        <span class="icon">🖼️</span>
                        <p>L'aperçu de l'ordonnance<br>apparaîtra ici</p>
                        <p style="font-size:0.7rem; margin-top:0.5rem;">Téléchargez une image ou un PDF</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # ---- Historique des scans ----
        st.markdown("---")
        st.subheader("📋 Ordonnances scannees recentes")
        
        scans = db.get_scans_recents(limit=15)
        
        if not scans:
            st.info("ℹ️ Aucune ordonnance scannee pour le moment.")
        else:
            couleurs = {
                'EN_ATTENTE': ('#fffbeb', '#f59e0b'),
                'VALIDEE': ('#f0fdf4', '#22c55e'),
                'ANNULEE': ('#fef2f2', '#dc2626'),
            }
            
            for row in scans:
                analyse_id, date, patient_nom, statut, statut_validation, nb_alertes, meds = row
                bg, border = couleurs.get(statut_validation, ('#f8fafc', '#94a3b8'))
                
                st.markdown(f"""
                <div style="background:{bg}; padding:0.6rem 1rem; border-radius:8px; border-left:4px solid {border}; margin:0.3rem 0;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                        <div>
                            <strong>{patient_nom}</strong>
                            <span style="color:#64748b; font-size:0.75rem; margin-left:0.8rem;">{date}</span>
                        </div>
                        <div>
                            <span style="color:#64748b; font-size:0.75rem;">{meds or 'Aucun'}</span>
                            <span style="background:{border}; color:white; padding:0.1rem 0.6rem; border-radius:10px; font-size:0.6rem; font-weight:600; margin-left:0.5rem;">{statut_validation}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()