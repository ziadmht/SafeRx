import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class DatabaseManager:
    """Gestionnaire de connexion à la base de données"""

    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"

    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)

    def execute_query(self, query, params=None):
        """Exécute une requête et retourne les résultats"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        results = cursor.fetchall()
        conn.close()
        return results

    def execute_write(self, query, params=None):
        """Exécute une requête d'écriture (INSERT, UPDATE, DELETE)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def execute_query_paginated(self, query: str, params: tuple = None,
                               page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Exécute une requête avec pagination."""
        conn = self.get_connection()
        cursor = conn.cursor()

        count_query = query.replace("SELECT", "SELECT COUNT(*)", 1)
        if "ORDER BY" in count_query:
            count_query = count_query[:count_query.index("ORDER BY")]

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
            'page': page,
            'total_pages': total_pages,
            'page_size': page_size
        }

    def get_table_stats(self) -> Dict[str, int]:
        """Retourne les statistiques des tables."""
        conn = self.get_connection()
        cursor = conn.cursor()

        tables = ['Patient', 'Medicament', 'Molecule', 'Interaction', 'Allergie', 'Analyse']
        stats = {}

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]

        conn.close()
        return stats

# Test rapide
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Tester la connexion
    patients = db.execute_query("SELECT * FROM Patient")
    print("[TEST] Patients dans la base :")
    for patient in patients:
        print(f"  - {patient[1]} {patient[2]}")
    
    # Tester les médicaments
    medicaments = db.execute_query("SELECT nom FROM Medicament")
    print("\n[TEST] Medicaments disponibles :")
    for med in medicaments:
        print(f"  - {med[0]}")
