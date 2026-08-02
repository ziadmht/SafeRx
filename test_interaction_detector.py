# test_interaction_detector.py
import unittest
from src.core.interaction_detector import InteractionDetector, Alert, AnalyseResult

class TestInteractionDetector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.detector = InteractionDetector()

    def test_analyse_ordonnance_interaction(self):
        # Patient #1: Benjelloun Karim
        # Medicaments: 1 (Aspirine), 3 (Coumadine)
        # Should detect a severe/elevated interaction between Aspirine and Coumadine
        result = self.detector.analyser_ordonnance(1, [1, 3])
        
        self.assertEqual(result.patient_nom, "Benjelloun Karim")
        self.assertIn("Aspirine", result.medicaments)
        self.assertIn("Coumadine", result.medicaments)
        self.assertFalse(result.est_securise)
        self.assertGreater(len(result.alertes), 0)
        
        # Check interaction alert details
        interaction_alerts = [a for a in result.alertes if a.type_alerte == 'interaction']
        self.assertGreater(len(interaction_alerts), 0)
        self.assertEqual(interaction_alerts[0].niveau, 'Élevé')
        self.assertEqual(interaction_alerts[0].color, '🔴')

    def test_analyse_ordonnance_allergie(self):
        # Patient #1 is allergic to Pénicilline (molecule 7, Medicament Pénicilline G is 7)
        # Let's verify that prescribing Pénicilline G (id 7) to patient #1 triggers an allergy alert
        result = self.detector.analyser_ordonnance(1, [7])
        
        self.assertFalse(result.est_securise)
        allergy_alerts = [a for a in result.alertes if a.type_alerte == 'allergie']
        self.assertGreater(len(allergy_alerts), 0)
        self.assertEqual(allergy_alerts[0].niveau, 'Élevé')
        self.assertEqual(allergy_alerts[0].color, '🔴')

    def test_get_alternatives_for_medicament_with_lower_threshold(self):
        # Using a threshold of 0.25 (well adapted for French medical terms in all-MiniLM-L6-v2)
        # Should return alternatives for Aspirine
        alternatives = self.detector.get_alternatives_for_medicament("Aspirine", threshold=0.25)
        self.assertGreater(len(alternatives), 0)
        
        # Verify alternative results structure
        import numpy as np
        for name, score in alternatives:
            self.assertIsInstance(name, str)
            self.assertTrue(isinstance(score, (float, np.floating)))
            self.assertGreaterEqual(score, 0.25)

if __name__ == "__main__":
    unittest.main()
