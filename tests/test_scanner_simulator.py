# tests/test_scanner_simulator.py
import pytest
import json
import io
from src.core.scanner_simulator import ScannerSimulator


class TestScannerSimulator:
    """Tests pour ScannerSimulator."""

    def test_initialization(self):
        """Teste l'initialisation du ScannerSimulator."""
        scanner = ScannerSimulator()
        assert scanner is not None
        assert len(scanner.PATIENTS_CONNUS) == 5
        assert len(scanner.MEDICAMENTS_CONNUS) == 8

    def test_get_patients(self):
        """Teste la récupération des patients connus."""
        scanner = ScannerSimulator()
        patients = scanner.get_patients()
        assert isinstance(patients, dict)
        assert "123456789012345" in patients
        assert patients["123456789012345"]["nom"] == "Benjelloun"
        assert patients["123456789012345"]["prenom"] == "Karim"

    def test_get_medicaments(self):
        """Teste la récupération des médicaments connus."""
        scanner = ScannerSimulator()
        medicaments = scanner.get_medicaments()
        assert isinstance(medicaments, list)
        assert "Aspirine" in medicaments
        assert "Doliprane" in medicaments
        assert "Coumadine" in medicaments

    def test_lire_fichier_json_valide(self):
        """Teste la lecture d'un fichier JSON valide."""
        scanner = ScannerSimulator()
        
        # Créer un fichier JSON simulé
        data = {
            "nss": "123456789012345",
            "medicaments": ["Aspirine", "Coumadine"],
            "patient": {
                "nom": "Benjelloun",
                "prenom": "Karim",
                "dateNaissance": "1982-03-15",
                "sexe": "M",
                "telephone": "0612345678"
            }
        }
        fichier = io.BytesIO(json.dumps(data).encode('utf-8'))
        fichier.name = "ordonnance.json"
        
        result = scanner.lire_fichier(fichier)
        assert result["nss"] == "123456789012345"
        assert "Aspirine" in result["medicaments"]
        assert "Coumadine" in result["medicaments"]
        assert result["patient"]["nom"] == "Benjelloun"

    def test_lire_fichier_json_sans_patient(self):
        """Teste la lecture d'un fichier JSON sans données patient."""
        scanner = ScannerSimulator()
        
        data = {
            "nss": "123456789012345",
            "medicaments": ["Aspirine", "Doliprane"]
        }
        fichier = io.BytesIO(json.dumps(data).encode('utf-8'))
        fichier.name = "ordonnance.json"
        
        result = scanner.lire_fichier(fichier)
        assert result["nss"] == "123456789012345"
        assert "Aspirine" in result["medicaments"]
        # Le patient doit être enrichi depuis PATIENTS_CONNUS
        assert result["patient"]["nom"] == "Benjelloun"

    def test_lire_fichier_json_patient_inconnu(self):
        """Teste la lecture d'un fichier JSON avec un patient inconnu."""
        scanner = ScannerSimulator()
        
        data = {
            "nss": "999999999999999",
            "medicaments": ["Aspirine"],
            "patient": {
                "nom": "Inconnu",
                "prenom": "Test",
                "dateNaissance": "1990-01-01",
                "sexe": "M",
                "telephone": "0600000000"
            }
        }
        fichier = io.BytesIO(json.dumps(data).encode('utf-8'))
        fichier.name = "ordonnance.json"
        
        result = scanner.lire_fichier(fichier)
        assert result["nss"] == "999999999999999"
        assert result["patient"]["nom"] == "Inconnu"

    def test_lire_fichier_json_sans_nss(self):
        """Teste la lecture d'un fichier JSON sans NSS."""
        scanner = ScannerSimulator()
        
        data = {
            "medicaments": ["Aspirine", "Coumadine"],
            "patient": {
                "nom": "Test",
                "prenom": "SansNSS"
            }
        }
        fichier = io.BytesIO(json.dumps(data).encode('utf-8'))
        fichier.name = "ordonnance.json"
        
        with pytest.raises(ValueError, match="NSS"):
            scanner.lire_fichier(fichier)

    def test_lire_fichier_json_sans_medicaments(self):
        """Teste la lecture d'un fichier JSON sans médicaments."""
        scanner = ScannerSimulator()
        
        data = {
            "nss": "123456789012345",
            "patient": {
                "nom": "Test",
                "prenom": "SansMedicaments"
            }
        }
        fichier = io.BytesIO(json.dumps(data).encode('utf-8'))
        fichier.name = "ordonnance.json"
        
        with pytest.raises(ValueError, match="médicament"):
            scanner.lire_fichier(fichier)

    def test_lire_fichier_json_medicaments_vides(self):
        """Teste la lecture d'un fichier JSON avec une liste de médicaments vide."""
        scanner = ScannerSimulator()
        
        data = {
            "nss": "123456789012345",
            "medicaments": [],
            "patient": {
                "nom": "Test",
                "prenom": "MedicamentsVides"
            }
        }
        fichier = io.BytesIO(json.dumps(data).encode('utf-8'))
        fichier.name = "ordonnance.json"
        
        with pytest.raises(ValueError, match="médicament"):
            scanner.lire_fichier(fichier)

    def test_lire_fichier_json_avec_patient_complet(self):
        """Teste la lecture d'un fichier JSON avec un patient complet."""
        scanner = ScannerSimulator()
        
        data = {
            "nss": "234567890123456",
            "medicaments": ["Advil", "Voltarène"],
            "patient": {
                "nom": "El Amrani",
                "prenom": "Fatima",
                "dateNaissance": "1990-07-22",
                "sexe": "F",
                "telephone": "0623456789"
            }
        }
        fichier = io.BytesIO(json.dumps(data).encode('utf-8'))
        fichier.name = "ordonnance.json"
        
        result = scanner.lire_fichier(fichier)
        assert result["nss"] == "234567890123456"
        assert "Advil" in result["medicaments"]
        assert result["patient"]["nom"] == "El Amrani"
        assert result["patient"]["prenom"] == "Fatima"

    def test_patients_connus_complets(self):
        """Teste que tous les patients connus ont les bonnes informations."""
        scanner = ScannerSimulator()
        patients = scanner.get_patients()
        
        # Vérifier chaque patient
        for nss, info in patients.items():
            assert 'nom' in info
            assert 'prenom' in info
            assert 'dateNaissance' in info
            assert 'sexe' in info
            assert 'telephone' in info
            assert len(nss) == 15  # NSS doit faire 15 chiffres

    def test_parser_texte_ocr_ameliore(self):
        """Teste l'extraction intelligente du scanner OCR (séparation dosage, exclusion noms et en-têtes)."""
        from src.core.ocr_scanner import OCRScanner
        scanner = OCRScanner.__new__(OCRScanner)
        scanner.medicaments_ref = {
            "aspirine": "Aspirine",
            "coumadine": "Coumadine",
            "doliprane": "Doliprane"
        }
        
        texte_ordonnance = """
        ORDONNANCE MEDICALE
        NSS : 123456789012345
        - Aspirine 500mg
        Coumadine 5mg - 1 comprimé par jour
        Doliprane 1000 mg
        Dr. Mohamed Alaoui
        Date : 29/07/2026
        """
        
        resultat = scanner._parser_texte(texte_ordonnance)
        
        assert resultat["nss"] == "123456789012345"
        assert "Aspirine" in resultat["medicaments"]
        assert "Coumadine" in resultat["medicaments"]
        assert "Doliprane" in resultat["medicaments"]
        assert "Aspirine 500mg" not in resultat["medicaments"]
        assert "Dr. Mohamed Alaoui" not in resultat["medicaments"]
        assert len(resultat["medicaments"]) == 3