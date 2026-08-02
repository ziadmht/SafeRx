# src/app/pages/login.py
import streamlit as st
from src.auth.auth_manager import AuthManager

def show_login():
    """Page de connexion design ultime - Inspiration grands laboratoires."""
    
    st.markdown("""
    <style>
        /* ===== FOND ===== */
        .stApp {
            background: #f7fafc;
        }
        
        /* ===== CONTENEUR PRINCIPAL ===== */
        .login-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 1.5rem;
        }
        
        .login-container {
            max-width: 380px;
            width: 100%;
            padding: 2.8rem 2.8rem 2.2rem 2.8rem;
            background: white;
            border-radius: 24px;
            box-shadow: 0 4px 48px rgba(0, 0, 0, 0.04), 0 1px 4px rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(0, 0, 0, 0.02);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        /* ===== BANDE DÉCORATIVE ===== */
        .login-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #2b6cb0, #48bb78);
        }
        
        /* ===== EN-TÊTE ===== */
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-logo-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.8rem;
            margin-bottom: 0.2rem;
        }
        
        .login-icon {
            font-size: 2.2rem;
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #ebf5ff, #dbeafe);
            border-radius: 14px;
            box-shadow: 0 2px 12px rgba(43, 108, 176, 0.08);
        }
        
        .login-brand {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0a1628;
            letter-spacing: -0.5px;
        }
        
        .login-brand span {
            background: linear-gradient(135deg, #2b6cb0, #3182ce);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .login-tagline {
            font-size: 0.7rem;
            color: #a0aec0;
            font-weight: 400;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            margin-top: 0.1rem;
        }
        
        /* ===== SÉPARATEUR ===== */
        .login-divider {
            width: 28px;
            height: 2px;
            background: linear-gradient(90deg, #2b6cb0, #48bb78);
            margin: 0.8rem auto 1.8rem auto;
            border-radius: 2px;
        }
        
        /* ===== CHAMPS DE SAISIE ===== */
        .stTextInput {
            margin-bottom: 0.4rem;
        }
        
        .stTextInput label {
            font-size: 0.65rem !important;
            font-weight: 600 !important;
            color: #4a5568 !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 0.2rem !important;
        }
        
        .stTextInput > div {
            margin-top: 0 !important;
        }
        
        .stTextInput > div > div {
            border-radius: 10px !important;
            border: 1.5px solid #edf2f7 !important;
            background: #fafbfc !important;
            transition: all 0.25s ease !important;
            box-shadow: none !important;
            min-height: 42px !important;
        }
        
        .stTextInput > div > div:focus-within {
            border-color: #2b6cb0 !important;
            background: white !important;
            box-shadow: 0 0 0 3px rgba(43, 108, 176, 0.05) !important;
        }
        
        .stTextInput input {
            padding: 0.45rem 1rem !important;
            font-size: 0.88rem !important;
            color: #1a202c !important;
            background: transparent !important;
        }
        
        .stTextInput input::placeholder {
            color: #a0aec0 !important;
            font-weight: 300 !important;
            font-size: 0.85rem !important;
        }
        
        /* ===== BOUTON ===== */
        .stButton {
            margin-top: 0.2rem;
        }
        
        .stButton button {
            background: #2b6cb0 !important;
            color: white !important;
            border: none !important;
            padding: 0.65rem 2rem !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            box-shadow: 0 2px 12px rgba(43, 108, 176, 0.12) !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            letter-spacing: 0.3px;
        }
        
        .stButton button:hover {
            background: #1a4f8b !important;
            box-shadow: 0 4px 20px rgba(43, 108, 176, 0.2) !important;
            transform: translateY(-1px) !important;
        }
        
        .stButton button:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 8px rgba(43, 108, 176, 0.12) !important;
        }
        
        /* ===== EXPANDER ===== */
        .streamlit-expanderHeader {
            font-size: 0.7rem !important;
            color: #a0aec0 !important;
            font-weight: 400 !important;
            padding: 0.3rem 0 !important;
            border-bottom: none !important;
            justify-content: center !important;
            gap: 0.3rem;
        }
        
        .streamlit-expanderHeader:hover {
            color: #2b6cb0 !important;
        }
        
        .streamlit-expanderHeader .icon {
            font-size: 0.8rem;
        }
        
        .streamlit-expanderContent {
            background: #f7fafc !important;
            border-radius: 10px !important;
            padding: 0.8rem !important;
            border: 1px solid #edf2f7 !important;
        }
        
        /* ===== META ===== */
        .login-meta {
            display: flex;
            justify-content: center;
            gap: 1.2rem;
            margin-top: 1.2rem;
            flex-wrap: wrap;
        }
        
        .login-meta-item {
            color: #a0aec0;
            font-size: 0.58rem;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        
        .login-meta-item .dot {
            display: inline-block;
            width: 4px;
            height: 4px;
            background: #48bb78;
            border-radius: 50%;
        }
        
        /* ===== FOOTER ===== */
        .login-footer {
            text-align: center;
            color: #a0aec0;
            font-size: 0.6rem;
            margin-top: 1.2rem;
            padding-top: 1rem;
            border-top: 1px solid #edf2f7;
            display: flex;
            justify-content: center;
            gap: 0.8rem;
            flex-wrap: wrap;
        }
        
        .login-footer .highlight {
            color: #2b6cb0;
            font-weight: 500;
        }
        
        .login-footer .sep {
            color: #e2e8f0;
        }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 480px) {
            .login-container {
                padding: 1.8rem;
                border-radius: 18px;
            }
            .login-brand {
                font-size: 1.5rem;
            }
            .login-icon {
                width: 44px;
                height: 44px;
                font-size: 1.8rem;
            }
            .login-logo-wrap {
                gap: 0.5rem;
            }
            .stTextInput input {
                padding: 0.35rem 0.8rem !important;
                font-size: 0.82rem !important;
            }
            .stTextInput > div > div {
                min-height: 38px !important;
            }
            .stButton button {
                padding: 0.55rem 1.5rem !important;
                font-size: 0.82rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # CONTENU
    # ============================================================
    st.markdown("""
    <div class="login-wrapper">
        <div class="login-container">
            <div class="login-header">
                <div class="login-logo-wrap">
                    <div class="login-icon">⚕️</div>
                    <div class="login-brand">Safe<span>Rx</span></div>
                </div>
                <div class="login-tagline">Intelligence Clinique</div>
                <div class="login-divider"></div>
            </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # FORMULAIRE
    # ============================================================
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="admin@saferx.com")
        password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
        
        submitted = st.form_submit_button("Se connecter", use_container_width=True)
        
        if submitted:
            if not email or not password:
                st.error("⚠️ Tous les champs sont requis.")
            else:
                auth = AuthManager()
                user = auth.login(email, password)
                
                if user:
                    st.session_state.user = user
                    st.success(f"✅ Bienvenue {user['prenom']} {user['nom']}")
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects.")

    # ============================================================
    # COMPTES DÉMO
    # ============================================================
    with st.expander("ℹ️ Comptes de démonstration"):
        st.markdown("""
        <div style="display:flex; flex-direction:column; gap:0.4rem; font-size:0.75rem;">
            <div style="display:flex; align-items:center; justify-content:space-between; padding:0.3rem 0.6rem; background:#ebf5ff; border-radius:6px;">
                <span style="font-weight:600; color:#2b6cb0; font-size:0.7rem;">👑 Admin</span>
                <span style="font-size:0.7rem; color:#4a5568;"><code style="background:white; padding:0.1rem 0.4rem; border-radius:3px; font-size:0.65rem;">admin@saferx.com</code></span>
                <span style="font-size:0.7rem; color:#4a5568;"><code style="background:white; padding:0.1rem 0.4rem; border-radius:3px; font-size:0.65rem;">admin123</code></span>
            </div>
            <div style="display:flex; align-items:center; justify-content:space-between; padding:0.3rem 0.6rem; background:#f0fff4; border-radius:6px;">
                <span style="font-weight:600; color:#48bb78; font-size:0.7rem;">💊 Pharmacien</span>
                <span style="font-size:0.7rem; color:#4a5568;"><code style="background:white; padding:0.1rem 0.4rem; border-radius:3px; font-size:0.65rem;">pharmacien@saferx.com</code></span>
                <span style="font-size:0.7rem; color:#4a5568;"><code style="background:white; padding:0.1rem 0.4rem; border-radius:3px; font-size:0.65rem;">pharmacien123</code></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # META
    # ============================================================
    st.markdown("""
    <div class="login-meta">
        <span class="login-meta-item"><span class="dot"></span> Sécurisé</span>
        <span class="login-meta-item">RGPD</span>
        <span class="login-meta-item">SmartRx</span>
        <span class="login-meta-item">100% Local</span>
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # FOOTER
    # ============================================================
    st.markdown("""
    <div class="login-footer">
        <span class="highlight">SafeRx</span>
        <span class="sep">·</span>
        <span>v2.0</span>
        <span class="sep">·</span>
        <span>Optimized NLP</span>
    </div>
    </div></div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    show_login()