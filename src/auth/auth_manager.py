# src/auth/auth_manager.py
import hashlib
import sqlite3
from pathlib import Path
from typing import Optional, Dict
import streamlit as st

class AuthManager:
    """Gestionnaire d'authentification pour SafeRx."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
        self.db_path = db_path
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            hashed = self._hash_password(password)
            
            cursor.execute("""
                SELECT id, email, nom, prenom, role, date_creation
                FROM Utilisateur
                WHERE email = ? AND mot_de_passe = ?
            """, (email, hashed))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'email': user[1],
                    'nom': user[2],
                    'prenom': user[3],
                    'role': user[4],
                    'date_creation': user[5]
                }
            return None
        except Exception as e:
            print(f"⚠️ Erreur de login: {e}")
            return None
    
    def logout(self):
        if 'user' in st.session_state:
            del st.session_state.user
        st.rerun()
    
    def is_authenticated(self) -> bool:
        return 'user' in st.session_state and st.session_state.user is not None
    
    def get_current_user(self) -> Optional[Dict]:
        return st.session_state.get('user', None)
    
    def is_admin(self) -> bool:
        user = self.get_current_user()
        return user is not None and user.get('role') == 'Admin'
    
    def is_pharmacien(self) -> bool:
        user = self.get_current_user()
        return user is not None and user.get('role') == 'Pharmacien'
    
    def require_auth(self):
        if not self.is_authenticated():
            st.error("🔒 Veuillez vous connecter.")
            st.stop()
    
    def require_admin(self):
        self.require_auth()
        if not self.is_admin():
            st.error("⛔ Accès réservé aux Administrateurs.")
            st.stop()
    
    def get_all_users(self) -> list:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, nom, prenom, role, date_creation
                FROM Utilisateur
                ORDER BY date_creation DESC
            """)
            users = cursor.fetchall()
            conn.close()
            return [
                {
                    'id': u[0],
                    'email': u[1],
                    'nom': u[2],
                    'prenom': u[3],
                    'role': u[4],
                    'date_creation': u[5]
                }
                for u in users
            ]
        except:
            return []
    
    def add_user(self, email: str, password: str, nom: str, prenom: str, role: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            hashed = self._hash_password(password)
            cursor.execute("""
                INSERT INTO Utilisateur (email, mot_de_passe, nom, prenom, role)
                VALUES (?, ?, ?, ?, ?)
            """, (email, hashed, nom, prenom, role))
            conn.commit()
            conn.close()
            return True
        except:
            return False