# tests/test_patient_manager.py
import pytest
import sqlite3
from src.core.patient_manager import PatientManager


class TestPatientManager:
    """Tests pour PatientManager."""

    def test_initialization(self, test_db):
        pm = PatientManager(db_path=test_db)
        assert pm is not None
        assert pm.db_path == test_db

    def test_get_all(self, test_db):
        pm = PatientManager(db_path=test_db)
        patients = pm.get_all()
        assert isinstance(patients, list)
        assert len(patients) >= 5

    def test_get_by_id(self, test_db):
        pm = PatientManager(db_path=test_db)
        patient = pm.get_by_id(1)
        assert patient is not None
        assert patient['nom'] == "Benjelloun"
        assert patient['nss'] == "123456789012345"

    def test_get_by_id_inexistant(self, test_db):
        pm = PatientManager(db_path=test_db)
        patient = pm.get_by_id(999)
        assert patient is None

    def test_get_by_nss(self, test_db):
        pm = PatientManager(db_path=test_db)
        patient = pm.get_by_nss("123456789012345")
        assert patient is not None
        assert patient['nom'] == "Benjelloun"

    def test_get_by_nss_inexistant(self, test_db):
        pm = PatientManager(db_path=test_db)
        patient = pm.get_by_nss("999999999999999")
        assert patient is None

    def test_get_or_create_by_nss_existant(self, test_db):
        pm = PatientManager(db_path=test_db)
        patient = pm.get_or_create_by_nss("123456789012345")
        assert patient is not None
        assert patient['nom'] == "Benjelloun"

    def test_get_or_create_by_nss_nouveau(self, test_db):
        pm = PatientManager(db_path=test_db)
        # ✅ Utiliser un NSS vraiment unique
        import time
        nss_unique = f"999888777666{int(time.time()) % 1000:03d}"
        patient_data = {
            'nom': 'Test',
            'prenom': 'Creation',
            'dateNaissance': '1990-01-01',
            'sexe': 'M',
            'telephone': '0600000000'
        }
        patient = pm.get_or_create_by_nss(nss_unique, patient_data)
        assert patient is not None
        assert patient['nss'] == nss_unique
        assert patient['nom'] == "Test"

    def test_get_or_create_by_nss_sans_donnees(self, test_db):
        pm = PatientManager(db_path=test_db)
        import time
        nss_unique = f"111222333444{int(time.time()) % 1000:03d}"
        patient = pm.get_or_create_by_nss(nss_unique)
        assert patient is not None
        assert patient['nss'] == nss_unique
        assert patient['nom'] == "Inconnu"

    def test_add_patient(self, test_db):
        pm = PatientManager(db_path=test_db)
        import time
        nss_unique = f"999888777666{int(time.time()) % 1000:03d}"
        
        patient_id = pm.add(
            nss=nss_unique,
            nom="Dupont",
            prenom="Jean",
            dateNaissance="1985-05-15",
            sexe="M",
            telephone="0612345678"
        )
        assert patient_id > 0
        
        patient = pm.get_by_id(patient_id)
        assert patient is not None
        assert patient['nom'] == "Dupont"

    def test_update_patient(self, test_db):
        pm = PatientManager(db_path=test_db)
        import time
        nss_unique = f"888777666555{int(time.time()) % 1000:03d}"
        
        patient_id = pm.add(
            nss=nss_unique,
            nom="Martin",
            prenom="Sophie",
            dateNaissance="1990-03-20",
            sexe="F",
            telephone="0678901234"
        )
        
        result = pm.update(
            patient_id,
            nss=nss_unique,
            nom="Martin",
            prenom="Sophie",
            dateNaissance="1990-03-20",
            sexe="F",
            telephone="0698765432"
        )
        assert result is True
        
        patient = pm.get_by_id(patient_id)
        assert patient['telephone'] == "0698765432"

    def test_update_patient_inexistant(self, test_db):
        pm = PatientManager(db_path=test_db)
        result = pm.update(
            999,
            nss="111222333444555",
            nom="Inexistant",
            prenom="Test",
            dateNaissance="1990-01-01",
            sexe="M",
            telephone="0600000000"
        )
        assert result is False

    def test_delete_patient(self, test_db):
        pm = PatientManager(db_path=test_db)
        import time
        nss_unique = f"777666555444{int(time.time()) % 1000:03d}"
        
        patient_id = pm.add(
            nss=nss_unique,
            nom="Test",
            prenom="Suppression",
            dateNaissance="2000-01-01",
            sexe="M",
            telephone="0612345678"
        )
        
        result = pm.delete(patient_id)
        assert result is True
        
        patient = pm.get_by_id(patient_id)
        assert patient is None

    def test_delete_patient_inexistant(self, test_db):
        pm = PatientManager(db_path=test_db)
        result = pm.delete(999)
        assert result is False

    def test_get_allergies(self, test_db):
        pm = PatientManager(db_path=test_db)
        allergies = pm.get_allergies(1)
        assert isinstance(allergies, list)
        assert len(allergies) >= 1

    def test_add_allergie(self, test_db):
        pm = PatientManager(db_path=test_db)
        
        # Vérifier les allergies existantes
        allergies_avant = pm.get_allergies(1)
        
        # Ajouter une allergie
        result = pm.add_allergie(
            patient_id=1,
            molecule_id=1,  # Acide acétylsalicylique
            type_alle="Médicament",
            gravite="Moyenne"
        )
        assert result is True
        
        # Vérifier que l'allergie a été ajoutée
        allergies_apres = pm.get_allergies(1)
        assert len(allergies_apres) > len(allergies_avant)

    def test_delete_allergie(self, test_db):
        pm = PatientManager(db_path=test_db)
        
        # Ajouter une allergie
        pm.add_allergie(1, 1, "Médicament", "Moyenne")
        
        # Récupérer les allergies
        allergies = pm.get_allergies(1)
        assert len(allergies) > 0
        
        # Supprimer la dernière allergie ajoutée
        result = pm.delete_allergie(1, allergies[-1]['id'])
        assert result is True

    def test_get_molecules(self, test_db):
        pm = PatientManager(db_path=test_db)
        molecules = pm.get_molecules()
        assert isinstance(molecules, list)
        assert len(molecules) >= 8

    def test_get_statistics(self, test_db):
        pm = PatientManager(db_path=test_db)
        stats = pm.get_statistics()
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'sexe_distribution' in stats
        assert 'with_allergies' in stats
        assert 'without_allergies' in stats
        assert stats['total'] >= 5