# tests/conftest.py - Version complète corrigée
import pytest
import sys
from pathlib import Path
import sqlite3
import tempfile
import shutil
import time

# Ajouter le dossier src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.init_db import init_database
from src.nlp.semantic_engine import SemanticEngine
from src.nlp.optimized_semantic_engine import OptimizedSemanticEngine
from src.nlp.embedding_engine import EmbeddingEngine
from src.core.interaction_detector import InteractionDetector
from src.core.history_manager import HistoryManager
from src.database.db_manager import DatabaseManager


# ============================================================
# FIXTURES DE BASE DE DONNÉES
# ============================================================

@pytest.fixture(scope="function")
def test_db():
    """Crée une base de données de test temporaire."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_saferx.db"
    
    # ✅ Initialiser avec init_database
    try:
        init_database(db_path)
    except Exception as e:
        print(f"⚠️ init_database échoué: {e}")
        # Créer la BDD manuellement
        conn = sqlite3.connect(db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS Patient (
                idPatient INTEGER PRIMARY KEY AUTOINCREMENT,
                nss VARCHAR(15) UNIQUE,
                nom VARCHAR(50) NOT NULL,
                prenom VARCHAR(50) NOT NULL,
                dateNaissance DATE,
                sexe CHAR(1) CHECK (sexe IN ('M', 'F')),
                telephone VARCHAR(15)
            );
            CREATE TABLE IF NOT EXISTS Medicament (
                idMedicament INTEGER PRIMARY KEY AUTOINCREMENT,
                nom VARCHAR(100) NOT NULL,
                codeCIS VARCHAR(15) UNIQUE,
                forme VARCHAR(50),
                dosage VARCHAR(20),
                prix DECIMAL(10,2)
            );
            CREATE TABLE IF NOT EXISTS Molecule (
                idMolecule INTEGER PRIMARY KEY AUTOINCREMENT,
                nom VARCHAR(100) NOT NULL,
                famille VARCHAR(50),
                formule VARCHAR(50)
            );
            CREATE TABLE IF NOT EXISTS Medicament_Molecule (
                idMedicament INTEGER,
                idMolecule INTEGER,
                PRIMARY KEY (idMedicament, idMolecule),
                FOREIGN KEY (idMedicament) REFERENCES Medicament(idMedicament),
                FOREIGN KEY (idMolecule) REFERENCES Molecule(idMolecule)
            );
            CREATE TABLE IF NOT EXISTS Interaction (
                idInteraction INTEGER PRIMARY KEY AUTOINCREMENT,
                idMolecule1 INTEGER NOT NULL,
                idMolecule2 INTEGER NOT NULL,
                niveau VARCHAR(10) CHECK (niveau IN ('ELEVE', 'MOYEN', 'FAIBLE')),
                description TEXT,
                recommandation TEXT,
                FOREIGN KEY (idMolecule1) REFERENCES Molecule(idMolecule),
                FOREIGN KEY (idMolecule2) REFERENCES Molecule(idMolecule)
            );
            CREATE TABLE IF NOT EXISTS Allergie (
                idAllergie INTEGER PRIMARY KEY AUTOINCREMENT,
                idPatient INTEGER NOT NULL,
                idMolecule INTEGER NOT NULL,
                type VARCHAR(50),
                gravite VARCHAR(20) CHECK (gravite IN ('Légère', 'Moyenne', 'Sévère')),
                FOREIGN KEY (idPatient) REFERENCES Patient(idPatient),
                FOREIGN KEY (idMolecule) REFERENCES Molecule(idMolecule)
            );
            CREATE TABLE IF NOT EXISTS Analyse (
                idAnalyse INTEGER PRIMARY KEY AUTOINCREMENT,
                idPatient INTEGER NOT NULL,
                dateAnalyse DATETIME DEFAULT CURRENT_TIMESTAMP,
                statut VARCHAR(10) CHECK (statut IN ('SECURISEE', 'ALERTE', 'ANNULEE')),
                nb_alertes INTEGER DEFAULT 0,
                nb_interactions INTEGER DEFAULT 0,
                nb_allergies INTEGER DEFAULT 0,
                statut_validation VARCHAR(10) DEFAULT 'EN_ATTENTE',
                date_validation DATETIME,
                idFacture INTEGER,
                FOREIGN KEY (idPatient) REFERENCES Patient(idPatient)
            );
            CREATE TABLE IF NOT EXISTS Alerte_Historique (
                idAlerte INTEGER PRIMARY KEY AUTOINCREMENT,
                idAnalyse INTEGER NOT NULL,
                type_alerte VARCHAR(20) CHECK (type_alerte IN ('interaction', 'allergie', 'information')),
                niveau VARCHAR(10) CHECK (niveau IN ('ELEVE', 'MOYEN', 'FAIBLE')),
                message TEXT,
                description TEXT,
                recommandation TEXT,
                medicaments_concernee TEXT,
                FOREIGN KEY (idAnalyse) REFERENCES Analyse(idAnalyse)
            );
            CREATE TABLE IF NOT EXISTS Analyse_Medicament (
                idAnalyse INTEGER,
                idMedicament INTEGER,
                PRIMARY KEY (idAnalyse, idMedicament),
                FOREIGN KEY (idAnalyse) REFERENCES Analyse(idAnalyse),
                FOREIGN KEY (idMedicament) REFERENCES Medicament(idMedicament)
            );
            CREATE TABLE IF NOT EXISTS Utilisateur (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(100) NOT NULL UNIQUE,
                mot_de_passe VARCHAR(255) NOT NULL,
                nom VARCHAR(50) NOT NULL,
                prenom VARCHAR(50) NOT NULL,
                role VARCHAR(20) CHECK (role IN ('Admin', 'Pharmacien')),
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()
    
    # ✅ Ajouter les données de test avec valeurs ASCII
    conn = sqlite3.connect(db_path)
    conn.executescript("""
        -- Insertion des molécules
        INSERT OR IGNORE INTO Molecule (idMolecule, nom, famille, formule) VALUES
        (1, 'Acide acétylsalicylique', 'AINS', 'C9H8O4'),
        (2, 'Paracétamol', 'Antalgique', 'C8H9NO2'),
        (3, 'Warfarine', 'Anticoagulant', 'C19H16O4'),
        (4, 'Ibuprofène', 'AINS', 'C13H18O2'),
        (5, 'Amoxicilline', 'Pénicilline', 'C16H19N3O5S'),
        (6, 'Diclofénac', 'AINS', 'C14H11Cl2NO2'),
        (7, 'Pénicilline', 'Antibiotique', 'C16H18N2O4S'),
        (8, 'Oméprazole', 'IPP', 'C17H19N3O3S');

        -- Insertion des médicaments
        INSERT OR IGNORE INTO Medicament (idMedicament, nom, codeCIS, forme, dosage, prix) VALUES
        (1, 'Aspirine', '123456', 'Comprimé', '500mg', 15.00),
        (2, 'Doliprane', '234567', 'Comprimé', '500mg', 20.00),
        (3, 'Coumadine', '345678', 'Comprimé', '5mg', 45.00),
        (4, 'Advil', '456789', 'Comprimé', '400mg', 25.00),
        (5, 'Amoxicilline Sandoz', '567890', 'Gélule', '500mg', 30.00),
        (6, 'Voltarène', '678901', 'Comprimé', '50mg', 35.00),
        (7, 'Pénicilline G', '789012', 'Injection', '1MUI', 40.00),
        (8, 'Mopral', '890123', 'Gélule', '20mg', 28.00);

        -- Insertion des médicaments → molécules
        INSERT OR IGNORE INTO Medicament_Molecule (idMedicament, idMolecule) VALUES
        (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8);

        -- ✅ CORRECTION : Insertion des interactions avec valeurs ASCII
        INSERT OR IGNORE INTO Interaction (idMolecule1, idMolecule2, niveau, description, recommandation) VALUES
        (1, 3, 'ELEVE', 'L''aspirine augmente le risque hémorragique de la warfarine', 'Surveillance étroite, éviter si possible'),
        (3, 4, 'MOYEN', 'L''ibuprofène augmente le risque hémorragique de la warfarine', 'Surveillance renforcée'),
        (1, 4, 'FAIBLE', 'Interaction entre AINS', 'Surveillance standard'),
        (5, 7, 'ELEVE', 'Allergie croisée possible entre pénicillines', 'À éviter en cas d''allergie'),
        (1, 5, 'FAIBLE', 'L''aspirine peut diminuer l''effet de l''amoxicilline', 'Surveillance');

        -- Insertion des patients
        INSERT OR IGNORE INTO Patient (idPatient, nss, nom, prenom, dateNaissance, sexe, telephone) VALUES
        (1, '123456789012345', 'Benjelloun', 'Karim', '1982-03-15', 'M', '0612345678'),
        (2, '234567890123456', 'El Amrani', 'Fatima', '1990-07-22', 'F', '0623456789'),
        (3, '345678901234567', 'Alaoui', 'Mohammed', '1975-11-10', 'M', '0634567890'),
        (4, '456789012345678', 'Tazi', 'Sofia', '2000-05-05', 'F', '0645678901'),
        (5, '567890123456789', 'Bennis', 'Omar', '1952-09-30', 'M', '0656789012');

        -- Insertion des allergies
        INSERT OR IGNORE INTO Allergie (idPatient, idMolecule, type, gravite) VALUES
        (1, 7, 'Médicament', 'Sévère'),
        (2, 1, 'Médicament', 'Moyenne'),
        (4, 5, 'Médicament', 'Sévère');
    """)
    conn.commit()
    conn.close()
    
    yield db_path
    
    # ✅ Nettoyage
    time.sleep(0.1)
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except PermissionError:
        time.sleep(0.5)
        shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================
# FIXTURES POUR LES COMPOSANTS
# ============================================================

@pytest.fixture
def semantic_engine(test_db):
    """Fournit une instance de SemanticEngine avec la base de test."""
    return SemanticEngine(db_path=test_db, auto_create=True)


@pytest.fixture
def optimized_semantic_engine(test_db):
    """Fournit une instance de OptimizedSemanticEngine avec la base de test."""
    return OptimizedSemanticEngine(db_path=test_db, precompute=True)


@pytest.fixture
def interaction_detector(test_db):
    """Fournit un détecteur d'interactions."""
    return InteractionDetector(engine_class=OptimizedSemanticEngine)


@pytest.fixture
def history_manager(test_db):
    """Fournit un gestionnaire d'historique."""
    return HistoryManager(db_path=test_db)


@pytest.fixture
def db_manager(test_db):
    """Fournit un gestionnaire de base de données."""
    return DatabaseManager(str(test_db))


# ============================================================
# FIXTURES DE DONNÉES
# ============================================================

@pytest.fixture
def sample_patient_data():
    """Retourne des données patient de test."""
    return {
        "id": 1,
        "nom": "Benjelloun",
        "prenom": "Karim",
        "dateNaissance": "1982-03-15",
        "sexe": "M",
        "telephone": "0612345678"
    }


@pytest.fixture
def sample_medicament_data():
    """Retourne des données médicament de test."""
    return {
        "id": 1,
        "nom": "Aspirine",
        "codeCIS": "123456",
        "forme": "Comprimé",
        "dosage": "500mg",
        "prix": 15.00
    }


@pytest.fixture
def sample_interaction_data():
    """Retourne des données interaction de test."""
    return {
        "molecule1": "Acide acétylsalicylique",
        "molecule2": "Warfarine",
        "niveau": "ELEVE",
        "description": "L'aspirine augmente le risque hémorragique",
        "recommandation": "Surveillance étroite"
    }


@pytest.fixture
def embedding_engine():
    """Fournit un moteur d'embeddings pour les tests."""
    return EmbeddingEngine()


@pytest.fixture
def scanner_simulator():
    """Fournit un simulateur de scanner."""
    from src.core.scanner_simulator import ScannerSimulator
    return ScannerSimulator()