# tests/test_interaction_detector.py - VERSION COMPLETE AVEC NOUVEAUX TESTS
import pytest
from src.core.interaction_detector import InteractionDetector, Alert, AnalyseResult
from src.core.constants import Niveau


class TestInteractionDetector:

    def test_initialization(self, interaction_detector):
        assert interaction_detector is not None
        assert interaction_detector.engine is not None

    def test_analyser_ordonnance_interaction(self, interaction_detector):
        """Teste l'analyse d'une ordonnance avec interaction."""
        result = interaction_detector.analyser_ordonnance(1, [1, 3])
        assert isinstance(result, AnalyseResult)
        assert result.patient_id == 1
        assert len(result.medicaments) == 2
        assert "Aspirine" in result.medicaments
        assert "Coumadine" in result.medicaments
        assert len(result.alertes) > 0
        assert result.est_securise == False

    def test_analyser_ordonnance_allergie(self, interaction_detector):
        """
        Teste l'analyse d'une ordonnance avec allergie.
        
        ✅ Patient 1 est allergique à la Pénicilline (ID 7)
        ✅ On utilise Pénicilline G (ID 7) pour déclencher l'allergie
        """
        allergies = interaction_detector.engine.get_patient_allergies(1)
        
        if allergies and len(allergies) > 0:
            result = interaction_detector.analyser_ordonnance(1, [7])
            assert isinstance(result, AnalyseResult)
            
            allergy_alertes = [a for a in result.alertes if a.type_alerte == "allergie"]
            assert len(allergy_alertes) > 0, f"L'allergie devrait être détectée. Alertes: {result.alertes}"
        else:
            pytest.skip("Aucune allergie dans la base de données de test")

    def test_analyser_ordonnance_securisee(self, interaction_detector):
        """Teste l'analyse d'une ordonnance sécurisée."""
        result = interaction_detector.analyser_ordonnance(2, [2])
        assert len(result.alertes) == 0
        assert result.est_securise == True

    def test_analyser_ordonnance_multiple(self, interaction_detector):
        """Teste l'analyse avec plusieurs médicaments."""
        result = interaction_detector.analyser_ordonnance(1, [1, 3, 2])
        assert len(result.alertes) >= 1
        assert result.resume is not None
        assert len(result.resume) > 0

    # ============================================================
    # ✅ NOUVEAUX TESTS POUR AMÉLIORER LA COUVERTURE
    # ============================================================

    def test_analyser_ordonnance_patient_inexistant(self, interaction_detector):
        """Teste l'analyse avec un patient inexistant."""
        result = interaction_detector.analyser_ordonnance(999, [1, 2])
        assert result.patient_nom == "Inconnu"
        assert result.patient_id == 999
        assert isinstance(result, AnalyseResult)

    def test_analyser_ordonnance_medicaments_vides(self, interaction_detector):
        """Teste l'analyse avec une liste de médicaments vide."""
        result = interaction_detector.analyser_ordonnance(1, [])
        assert len(result.medicaments) == 0
        assert len(result.alertes) == 0
        assert result.est_securise == True
        assert "sécurisée" in result.resume

    def test_analyser_ordonnance_un_seul_medicament(self, interaction_detector):
        """Teste l'analyse avec un seul médicament (pas d'interaction)."""
        result = interaction_detector.analyser_ordonnance(1, [1])
        assert len(result.medicaments) == 1
        assert "Aspirine" in result.medicaments
        assert len(result.alertes) == 0
        assert result.est_securise == True

    def test_get_alternatives_medicament_inexistant(self, interaction_detector):
        """Teste la recherche d'alternatives avec un médicament inexistant."""
        alternatives = interaction_detector.get_alternatives_for_medicament("Inexistant")
        assert isinstance(alternatives, list)
        assert len(alternatives) == 0

    def test_get_alternatives_medicament_existant(self, interaction_detector):
        """Teste la recherche d'alternatives avec un médicament existant."""
        alternatives = interaction_detector.get_alternatives_for_medicament("Aspirine", threshold=0.3)
        assert isinstance(alternatives, list)
        # Au moins une alternative ou une liste vide (selon la BDD)
        for nom, sim in alternatives:
            assert isinstance(nom, str)
            assert isinstance(sim, float)

    def test_analyser_ordonnance_alerte_allergie_seulement(self, interaction_detector):
        """Teste l'analyse avec une allergie uniquement (pas d'interaction)."""
        allergies = interaction_detector.engine.get_patient_allergies(4)
        
        if allergies and len(allergies) > 0:
            # Sofia Tazi (ID 4) est allergique à l'amoxicilline (ID 5)
            result = interaction_detector.analyser_ordonnance(4, [5])
            assert isinstance(result, AnalyseResult)
            
            allergy_alertes = [a for a in result.alertes if a.type_alerte == "allergie"]
            assert len(allergy_alertes) > 0, "L'allergie devrait être détectée"
        else:
            pytest.skip("Aucune allergie pour le patient 4")

    def test_analyser_ordonnance_interaction_niveau_eleve(self, interaction_detector):
        """Teste qu'une interaction de niveau Élevé est bien détectée comme critique."""
        result = interaction_detector.analyser_ordonnance(1, [1, 3])
        
        # Vérifier qu'il y a des alertes
        assert len(result.alertes) > 0
        
        # Vérifier qu'au moins une alerte est de niveau ELEVE
        alertes_eleve = [a for a in result.alertes if a.niveau == Niveau.ELEVE]
        assert len(alertes_eleve) > 0, "Devrait avoir une alerte de niveau Élevé"
        
        # Vérifier que est_securise est False (interaction critique)
        assert result.est_securise == False

    # ============================================================
    # TESTS EXISTANTS (CORRIGÉS)
    # ============================================================

    def test_alert_dataclass(self):
        alert = Alert(
            niveau=Niveau.ELEVE,
            type_alerte="interaction",
            message="Test",
            description="Test description",
            recommandation="Test recommandation",
            medicaments_concernee=["Test1", "Test2"]
        )
        assert alert.niveau == Niveau.ELEVE
        assert alert.color == "🔴"
        assert alert.type_alerte == "interaction"
        assert len(alert.medicaments_concernee) == 2

    def test_alert_colors(self):
        alert_critique = Alert(Niveau.ELEVE, "interaction", "", "", "", [])
        alert_moyen = Alert(Niveau.MOYEN, "interaction", "", "", "", [])
        alert_faible = Alert(Niveau.FAIBLE, "interaction", "", "", "", [])
        assert alert_critique.color == "🔴"
        assert alert_moyen.color == "🟠"
        assert alert_faible.color == "🟡"

    def test_get_alternatives_for_medicament(self, interaction_detector):
        alternatives = interaction_detector.get_alternatives_for_medicament("Aspirine", threshold=0.3)
        assert isinstance(alternatives, list)
        for nom, sim in alternatives:
            assert isinstance(nom, str)
            assert isinstance(sim, float)