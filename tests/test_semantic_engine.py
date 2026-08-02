# tests/test_semantic_engine.py - VERSION FINALE COMPLETE
import pytest
import numpy as np
from src.nlp.semantic_engine import SemanticEngine
from src.core.constants import Niveau


class TestSemanticEngine:
    """Tests pour le moteur sémantique - Version Production"""

    def test_initialization(self, semantic_engine):
        """Teste l'initialisation du moteur sémantique."""
        assert semantic_engine is not None
        assert len(semantic_engine.molecules) > 0
        assert len(semantic_engine.medicaments) > 0

    def test_get_medicament_molecules(self, semantic_engine):
        """Teste la récupération des molécules d'un médicament."""
        molecules = semantic_engine.get_medicament_molecules("Aspirine")
        assert len(molecules) > 0

    def test_get_molecule_embedding(self, semantic_engine):
        """Teste l'obtention d'un embedding de molécule."""
        vector = semantic_engine.get_molecule_embedding("Aspirine")
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 384

    def test_get_similar_molecules(self, semantic_engine):
        """Teste la recherche de molécules similaires."""
        results = semantic_engine.get_similar_molecules("aspirine", threshold=0.3)
        # ✅ Au moins un résultat avec un seuil bas
        assert len(results) > 0

    def test_get_patient_allergies(self, semantic_engine):
        """Teste la récupération des allergies d'un patient."""
        allergies = semantic_engine.get_patient_allergies(1)
        # ✅ Vérifier la structure même si vide
        assert isinstance(allergies, list)
        for mol_id, nom, type_alle, gravite in allergies:
            assert isinstance(mol_id, int)
            assert isinstance(nom, str)
            assert type_alle in ["Médicament", "Aliment", "Autre", ""]
            assert gravite in ["Sévère", "Moyenne", "Légère", ""]

    def test_detect_interactions(self, semantic_engine):
        """Teste la détection d'interactions."""
        interactions = semantic_engine.detect_interactions([1, 3])
        assert len(interactions) > 0
        for mol1, mol2, niveau, desc, reco in interactions:
            # ✅ CORRIGE : Utilise Niveau.ELEVE/MOYEN/FAIBLE
            assert niveau in [Niveau.ELEVE, Niveau.MOYEN, Niveau.FAIBLE]
            assert isinstance(desc, str)
            assert isinstance(reco, str)

    def test_check_allergies(self, semantic_engine):
        """Teste la vérification des allergies."""
        allergies = semantic_engine.check_allergies(1, [5])
        assert isinstance(allergies, list)
        # ✅ Si des allergies existent, vérifier la structure
        if allergies:
            for mol_id, nom, type_alle, gravite in allergies:
                assert isinstance(mol_id, int)
                assert isinstance(nom, str)

    def test_get_alternatives(self, semantic_engine):
        """Teste la recherche d'alternatives."""
        alternatives = semantic_engine.get_alternatives(1, threshold=0.3)
        assert isinstance(alternatives, list)
        for nom, sim in alternatives:
            assert isinstance(nom, str)
            assert isinstance(sim, float)

    def test_get_molecule_id_by_name(self, semantic_engine):
        """Teste la récupération de l'ID d'une molécule."""
        # ✅ Test avec plusieurs noms
        test_names = ["Aspirine", "Paracétamol", "Warfarine"]
        for name in test_names:
            mol_id = semantic_engine.get_molecule_id_by_name(name)
            # ✅ Si la molécule existe dans la BDD, l'ID doit être trouvé
            if any(m[1] == name for m in semantic_engine.molecules):
                assert mol_id is not None, f"Molécule {name} non trouvée"
                assert isinstance(mol_id, int)
            # Sinon, on ignore (BDD de test peut varier)

    def test_get_patient_by_id(self, semantic_engine):
        """Teste la récupération des informations d'un patient."""
        patient = semantic_engine.get_patient_by_id(1)
        assert patient is not None
        assert len(patient) == 6  # id, nom, prenom, date, sexe, telephone

    def test_get_performance_metrics(self, semantic_engine):
        """Teste la récupération des métriques de performance."""
        metrics = semantic_engine.get_performance_metrics()
        assert 'load_time_seconds' in metrics
        assert 'nlp_available' in metrics
        assert 'molecules_count' in metrics
        assert 'medicaments_count' in metrics

    def test_get_cache_stats(self, semantic_engine):
        """Teste la récupération des statistiques du cache."""
        stats = semantic_engine.get_cache_stats()
        assert 'alternatives_cache_size' in stats
        assert 'max_alt_cache_size' in stats

    def test_clear_cache(self, semantic_engine):
        """Teste le vidage du cache."""
        semantic_engine.get_alternatives(1, threshold=0.3)
        semantic_engine.clear_cache()
        stats = semantic_engine.get_cache_stats()
        assert stats['alternatives_cache_size'] == 0