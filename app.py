# app.py
import streamlit as st
from src.auth.auth_manager import AuthManager
from src.app.pages.login import show_login

if 'user' not in st.session_state:
    st.session_state.user = None
if 'app_initialized' not in st.session_state:
    st.session_state.app_initialized = False

st.set_page_config(
    page_title="SafeRx - Assistant Pharmacie",
    page_icon="🩺",
    layout="wide"
)

auth = AuthManager()

if not auth.is_authenticated():
    st.session_state.app_initialized = False
    show_login()
else:
    st.session_state.app_initialized = True
    from app_complete import main
    main()