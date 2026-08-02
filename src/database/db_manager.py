# src/database/db_manager.py
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

class DatabaseManager:
    """Gestionnaire de connexion à la base de données"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            self.db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
        else:
            self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ✅ ACTIVER LE MODE WAL POUR LES ÉCRITURES CONCURRENTES
        self._enable_wal()

    def _enable_wal(self):
        """Active le mode WAL et définit un timeout pour les accès concurrents."""
        try:
            conn = self.get_connection()
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=5000;")
            conn.close()
        except Exception as e:
            print(f"⚠️ Erreur lors de l'activation du mode WAL : {e}")

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
        finally:
            conn.close()
        return results

    def execute_write(self, query: str, params: Optional[tuple] = None) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            last_id = cursor.lastrowid
        finally:
            conn.close()
        return last_id

    # ✅ NOUVELLE MÉTHODE POUR LA TRANSACTION ATOMIQUE
    def execute_write_rowcount(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Exécute une requête d'écriture et retourne le nombre de lignes affectées.
        Utile pour les mises à jour atomiques (AND statut_validation = 'En attente').
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def execute_query_paginated(self, query: str, params: Optional[tuple] = None,
                               page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()

        match = re.search(r'\bFROM\b', query, re.IGNORECASE)
        if not match:
            count_query = f"SELECT COUNT(*) FROM ({query})"
        else:
            from_clause = query[match.start():]
            from_clause = re.split(r'\bORDER\s+BY\b', from_clause, flags=re.IGNORECASE)[0]
            from_clause = re.split(r'\bLIMIT\b', from_clause, flags=re.IGNORECASE)[0]
            count_query = "SELECT COUNT(*) " + from_clause.strip()

        cursor.execute(count_query, params or ())
        total = cursor.fetchone()[0]

        offset = (page - 1) * page_size
        paginated_query = f"{query} LIMIT {page_size} OFFSET {offset}"
        cursor.execute(paginated_query, params or ())
        data = cursor.fetchall()

        conn.close()

        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        return {
            'data': data,
            'total': total,
            'page': max(1, min(page, total_pages)),
            'total_pages': total_pages,
            'page_size': page_size
        }

    def get_table_stats(self) -> Dict[str, int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        tables = ['Patient', 'Medicament', 'Molecule', 'Interaction', 'Allergie', 'Analyse', 'Ordonnance']
        stats = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                stats[table] = 0
        conn.close()
        return stats

    # ============================================================
    # ✅ MÉTHODE POUR L'HISTORIQUE DES SCANS (J14 - SCAN AUTOMATIQUE)
    # ============================================================
    def get_scans_recents(self, limit: int = 15) -> List[tuple]:
        """
        Récupère l'historique des scans depuis la table Analyse.
        Utilisé par l'onglet "📷 Scan Automatique".
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.idAnalyse, a.dateAnalyse, 
                   p.nom || ' ' || p.prenom AS patient_nom,
                   a.statut, a.statut_validation, a.nb_alertes,
                   GROUP_CONCAT(DISTINCT m.nom) AS medicaments
            FROM Analyse a
            JOIN Patient p ON a.idPatient = p.idPatient
            LEFT JOIN Analyse_Medicament am ON a.idAnalyse = am.idAnalyse
            LEFT JOIN Medicament m ON am.idMedicament = m.idMedicament
            GROUP BY a.idAnalyse
            ORDER BY a.dateAnalyse DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results

    # ============================================================
    # ✅ MÉTHODE POUR LES FACTURES (J14)
    # ============================================================
    def get_factures_recents(self, limit: int = 20) -> List[tuple]:
        """
        Récupère les factures récentes.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT f.idFacture, f.numero, f.date_emission, f.montant_total, f.statut,
                   p.nom || ' ' || p.prenom AS patient_nom
            FROM Facture f
            JOIN Patient p ON f.idPatient = p.idPatient
            ORDER BY f.date_emission DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results