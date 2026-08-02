# tests/test_database.py
import pytest
import sqlite3
from src.database.db_manager import DatabaseManager


class TestDatabase:
    """Tests pour la base de données - Version Production"""

    def test_initialization(self, db_manager):
        """Teste l'initialisation du gestionnaire."""
        assert db_manager is not None
        assert db_manager.db_path is not None
        assert db_manager.db_path.exists()

    def test_get_connection(self, db_manager):
        """Teste la connexion à la base de données."""
        conn = db_manager.get_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_execute_query(self, db_manager):
        """Teste l'exécution d'une requête."""
        results = db_manager.execute_query("SELECT * FROM Patient")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_execute_write(self, db_manager):
        """Teste l'exécution d'une requête d'écriture."""
        last_id = db_manager.execute_write(
            "INSERT INTO Patient (nom, prenom) VALUES (?, ?)",
            ("Test", "Temp")
        )
        assert isinstance(last_id, int)
        assert last_id > 0
        
        # Nettoyer
        db_manager.execute_write("DELETE FROM Patient WHERE idPatient = ?", (last_id,))

    def test_execute_query_paginated(self, db_manager):
        """Teste la pagination des requêtes."""
        result = db_manager.execute_query_paginated(
            "SELECT * FROM Patient ORDER BY idPatient",
            page=1,
            page_size=10
        )
        
        assert isinstance(result, dict)
        assert 'data' in result
        assert 'total' in result
        assert 'page' in result
        assert 'total_pages' in result
        assert isinstance(result['data'], list)
        assert result['page'] == 1
        assert result['page_size'] == 10

    def test_get_table_stats(self, db_manager):
        """Teste la récupération des statistiques des tables."""
        stats = db_manager.get_table_stats()
        
        assert isinstance(stats, dict)
        assert 'Patient' in stats
        assert 'Medicament' in stats
        assert isinstance(stats['Patient'], int)
        assert stats['Patient'] >= 1

    def test_init_database(self, test_db):
        """Teste l'initialisation de la base de données."""
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['Patient', 'Medicament', 'Molecule', 'Interaction', 'Allergie']
        for table in required_tables:
            assert table in tables
        
        conn.close()