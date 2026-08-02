# tests/test_history_manager.py
import pytest
from datetime import datetime
from src.core.history_manager import HistoryManager


class TestHistoryManager:
    """Tests pour le gestionnaire d'historique."""

    def test_initialization(self, history_manager):
        """Teste l'initialisation du gestionnaire."""
        assert history_manager is not None
        assert history_manager.db_path is not None

    def test_create_tables_if_needed(self, history_manager):
        """Teste la création des tables."""
        history_manager._create_tables_if_needed()
        
        # Vérifier que les tables existent
        import sqlite3
        conn = sqlite3.connect(history_manager.db_path)
        cursor = conn.cursor()
        
        tables = ["Analyse", "Alerte_Historique", "Analyse_Medicament"]
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            assert cursor.fetchone() is not None
        
        conn.close()

    def test_get_statistiques(self, history_manager):
        """Teste la récupération des statistiques."""
        stats = history_manager.get_statistiques()
        
        assert isinstance(stats, dict)
        assert 'total_analyses' in stats
        assert 'par_statut' in stats
        assert isinstance(stats['total_analyses'], int)

    def test_get_performance_stats(self, history_manager):
        """Teste la récupération des statistiques de performance."""
        stats = history_manager.get_performance_stats()
        
        assert isinstance(stats, dict)
        assert 'total_analyses' in stats
        assert 'analyses_par_mois' in stats
        assert 'avg_response_time' in stats

    def test_enregistrer_analyse(self, history_manager, interaction_detector):
        """Teste l'enregistrement d'une analyse."""
        # Créer une analyse factice
        result = interaction_detector.analyser_ordonnance(1, [1, 3])
        
        # Enregistrer
        analyse_id = history_manager.enregistrer_analyse(1, [1, 3], result)
        
        assert analyse_id is not None
        assert isinstance(analyse_id, int)
        assert analyse_id > 0

    def test_get_historique(self, history_manager):
        """Teste la récupération de l'historique."""
        historique = history_manager.get_historique(limit=10)
        
        assert isinstance(historique, list)
        if len(historique) > 0:
            for item in historique:
                assert 'id' in item
                assert 'date' in item
                assert 'patient' in item
                assert 'statut' in item

    def test_get_historique_paginated(self, history_manager):
        """Teste la pagination de l'historique."""
        result = history_manager.get_historique_paginated(offset=0, limit=5)
        
        assert isinstance(result, dict)
        assert 'analyses' in result
        assert 'total' in result
        assert 'page' in result
        assert 'total_pages' in result
        assert isinstance(result['analyses'], list)

    def test_get_historique_paginated_filter(self, history_manager):
        """Teste la pagination avec filtre."""
        result = history_manager.get_historique_paginated(
            offset=0, 
            limit=5,
            statut_filter="Sécurisée"
        )
        
        assert isinstance(result, dict)
        # Vérifier que toutes les analyses filtrées ont le bon statut
        for analyse in result['analyses']:
            assert analyse['statut'] == "Sécurisée"

    def test_get_analyse_details(self, history_manager):
        """Teste la récupération des détails d'une analyse."""
        # D'abord récupérer une analyse existante
        historique = history_manager.get_historique(limit=1)
        
        if len(historique) > 0:
            analyse_id = historique[0]['id']
            details = history_manager.get_analyse_details(analyse_id)
            
            assert isinstance(details, dict)
            assert 'id' in details
            assert 'patient' in details
            assert 'statut' in details
            assert 'alertes' in details

    def test_get_total_analyses(self, history_manager):
        """Teste le comptage des analyses."""
        total = history_manager.get_total_analyses()
        assert isinstance(total, int)
        assert total >= 0
        
        # Avec filtre
        total_securise = history_manager.get_total_analyses(statut_filter="Sécurisée")
        assert isinstance(total_securise, int)
        assert total_securise <= total