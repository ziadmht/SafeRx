-- ============================================================
-- TABLE PATIENT
-- ============================================================
CREATE TABLE IF NOT EXISTS Patient (
    idPatient INTEGER PRIMARY KEY AUTOINCREMENT,
    nss VARCHAR(15) UNIQUE,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    dateNaissance DATE,
    sexe CHAR(1) CHECK (sexe IN ('M', 'F')),
    telephone VARCHAR(15)
);

-- ============================================================
-- TABLE MEDICAMENT
-- ============================================================
CREATE TABLE IF NOT EXISTS Medicament (
    idMedicament INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    codeCIS VARCHAR(15) UNIQUE,
    forme VARCHAR(50),
    dosage VARCHAR(20),
    prix DECIMAL(10,2)
);

-- ============================================================
-- TABLE MOLECULE
-- ============================================================
CREATE TABLE IF NOT EXISTS Molecule (
    idMolecule INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    famille VARCHAR(50),
    formule VARCHAR(50)
);

-- ============================================================
-- TABLE ORDONNANCE
-- ============================================================
CREATE TABLE IF NOT EXISTS Ordonnance (
    idOrdonnance INTEGER PRIMARY KEY AUTOINCREMENT,
    idPatient INTEGER NOT NULL,
    dateOrdonnance DATE DEFAULT CURRENT_DATE,
    statut VARCHAR(20) DEFAULT 'En attente',
    FOREIGN KEY (idPatient) REFERENCES Patient(idPatient)
);

-- ============================================================
-- TABLE ALLERGIE
-- ============================================================
CREATE TABLE IF NOT EXISTS Allergie (
    idAllergie INTEGER PRIMARY KEY AUTOINCREMENT,
    idPatient INTEGER NOT NULL,
    idMolecule INTEGER NOT NULL,
    type VARCHAR(50),
    gravite VARCHAR(20) CHECK (gravite IN ('Légère', 'Moyenne', 'Sévère')),
    FOREIGN KEY (idPatient) REFERENCES Patient(idPatient),
    FOREIGN KEY (idMolecule) REFERENCES Molecule(idMolecule)
);

-- ============================================================
-- TABLE INTERACTION (CORRIGEE)
-- ============================================================
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

-- ============================================================
-- TABLE ORDONNANCE_MEDICAMENT (Table de liaison)
-- ============================================================
CREATE TABLE IF NOT EXISTS Ordonnance_Medicament (
    idOrdonnance INTEGER,
    idMedicament INTEGER,
    dosage_prescrit VARCHAR(20),
    duree_traitement INTEGER,
    PRIMARY KEY (idOrdonnance, idMedicament),
    FOREIGN KEY (idOrdonnance) REFERENCES Ordonnance(idOrdonnance),
    FOREIGN KEY (idMedicament) REFERENCES Medicament(idMedicament)
);

-- ============================================================
-- TABLE MEDICAMENT_MOLECULE (Table de liaison)
-- ============================================================
CREATE TABLE IF NOT EXISTS Medicament_Molecule (
    idMedicament INTEGER,
    idMolecule INTEGER,
    PRIMARY KEY (idMedicament, idMolecule),
    FOREIGN KEY (idMedicament) REFERENCES Medicament(idMedicament),
    FOREIGN KEY (idMolecule) REFERENCES Molecule(idMolecule)
);

-- ============================================================
-- TABLES D'HISTORIQUE (JOUR 7)
-- ============================================================
-- ✅ CORRIGE : Analyse avec valeurs ASCII
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

-- ✅ CORRIGE : Alerte_Historique avec valeurs ASCII
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

-- ============================================================
-- TABLE FACTURE
-- ============================================================
CREATE TABLE IF NOT EXISTS Facture (
    idFacture INTEGER PRIMARY KEY AUTOINCREMENT,
    idAnalyse INTEGER NOT NULL UNIQUE,
    idPatient INTEGER NOT NULL,
    numero VARCHAR(50) NOT NULL UNIQUE,
    date_emission DATETIME DEFAULT CURRENT_TIMESTAMP,
    montant_total DECIMAL(10,2) NOT NULL,
    statut VARCHAR(20) CHECK (statut IN ('En attente', 'Payée', 'Annulée')),
    reference_paiement VARCHAR(50),
    date_paiement DATETIME,
    FOREIGN KEY (idAnalyse) REFERENCES Analyse(idAnalyse),
    FOREIGN KEY (idPatient) REFERENCES Patient(idPatient)
);

-- ============================================================
-- TABLE LIGNE FACTURE
-- ============================================================
CREATE TABLE IF NOT EXISTS LigneFacture (
    idLigne INTEGER PRIMARY KEY AUTOINCREMENT,
    idFacture INTEGER NOT NULL,
    idMedicament INTEGER NOT NULL,
    nom_medicament VARCHAR(100) NOT NULL,
    quantite INTEGER DEFAULT 1,
    prix_unitaire DECIMAL(10,2) NOT NULL,
    montant_ligne DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (idFacture) REFERENCES Facture(idFacture),
    FOREIGN KEY (idMedicament) REFERENCES Medicament(idMedicament)
);

-- ============================================================
-- TABLE UTILISATEUR (AUTHENTIFICATION)
-- ============================================================
CREATE TABLE IF NOT EXISTS Utilisateur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('Admin', 'Pharmacien')),
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INSERTION DES DONNÉES DE TEST
-- ============================================================

-- Suppression des anciennes données pour repartir sur une base propre
DELETE FROM Medicament_Molecule;
DELETE FROM Ordonnance_Medicament;
DELETE FROM Interaction;
DELETE FROM Allergie;
DELETE FROM Ordonnance;
DELETE FROM Patient;
DELETE FROM Medicament;
DELETE FROM Molecule;

-- INSERTION DES MOLÉCULES
INSERT OR IGNORE INTO Molecule (idMolecule, nom, famille, formule) VALUES
(1, 'Acide acétylsalicylique', 'AINS', 'C9H8O4'),
(2, 'Paracétamol', 'Antalgique', 'C8H9NO2'),
(3, 'Warfarine', 'Anticoagulant', 'C19H16O4'),
(4, 'Ibuprofène', 'AINS', 'C13H18O2'),
(5, 'Amoxicilline', 'Pénicilline', 'C16H19N3O5S'),
(6, 'Diclofénac', 'AINS', 'C14H11Cl2NO2'),
(7, 'Pénicilline', 'Antibiotique', 'C16H18N2O4S'),
(8, 'Oméprazole', 'IPP', 'C17H19N3O3S');

-- INSERTION DES MÉDICAMENTS
INSERT OR IGNORE INTO Medicament (idMedicament, nom, codeCIS, forme, dosage, prix) VALUES
(1, 'Aspirine', '123456', 'Comprimé', '500mg', 15.00),
(2, 'Doliprane', '234567', 'Comprimé', '500mg', 20.00),
(3, 'Coumadine', '345678', 'Comprimé', '5mg', 45.00),
(4, 'Advil', '456789', 'Comprimé', '400mg', 25.00),
(5, 'Amoxicilline Sandoz', '567890', 'Gélule', '500mg', 30.00),
(6, 'Voltarène', '678901', 'Comprimé', '50mg', 35.00),
(7, 'Pénicilline G', '789012', 'Injection', '1MUI', 40.00),
(8, 'Mopral', '890123', 'Gélule', '20mg', 28.00);

-- INSERTION DES MÉDICAMENTS → MOLÉCULES
INSERT OR IGNORE INTO Medicament_Molecule (idMedicament, idMolecule) VALUES
(1, 1), -- Aspirine → Acide acétylsalicylique
(2, 2), -- Doliprane → Paracétamol
(3, 3), -- Coumadine → Warfarine
(4, 4), -- Advil → Ibuprofène
(5, 5), -- Amoxicilline Sandoz → Amoxicilline
(6, 6), -- Voltarène → Diclofénac
(7, 7), -- Pénicilline G → Pénicilline
(8, 8); -- Mopral → Oméprazole

-- ✅ CORRIGE : INSERTION DES INTERACTIONS avec valeurs ASCII
INSERT OR IGNORE INTO Interaction (idMolecule1, idMolecule2, niveau, description, recommandation) VALUES
(1, 3, 'ELEVE', 'L''aspirine augmente le risque hémorragique de la warfarine', 'Surveillance étroite, éviter si possible'),
(3, 4, 'MOYEN', 'L''ibuprofène augmente le risque hémorragique de la warfarine', 'Surveillance renforcée'),
(1, 4, 'FAIBLE', 'Interaction entre AINS', 'Surveillance standard'),
(5, 7, 'ELEVE', 'Allergie croisée possible entre pénicillines', 'À éviter en cas d''allergie'),
(1, 5, 'FAIBLE', 'L''aspirine peut diminuer l''effet de l''amoxicilline', 'Surveillance');

-- INSERTION DES PATIENTS
INSERT OR IGNORE INTO Patient (idPatient, nss, nom, prenom, dateNaissance, sexe, telephone) VALUES
(1, '123456789012345', 'Benjelloun', 'Karim', '1982-03-15', 'M', '0612345678'),
(2, '234567890123456', 'El Amrani', 'Fatima', '1990-07-22', 'F', '0623456789'),
(3, '345678901234567', 'Alaoui', 'Mohammed', '1975-11-10', 'M', '0634567890'),
(4, '456789012345678', 'Tazi', 'Sofia', '2000-05-05', 'F', '0645678901'),
(5, '567890123456789', 'Bennis', 'Omar', '1952-09-30', 'M', '0656789012');

-- INSERTION DES ALLERGIES
INSERT OR IGNORE INTO Allergie (idPatient, idMolecule, type, gravite) VALUES
(1, 7, 'Médicament', 'Sévère'), -- Karim allergique à la pénicilline
(2, 1, 'Médicament', 'Moyenne'), -- Fatima allergique à l'aspirine
(4, 5, 'Médicament', 'Sévère'); -- Sofia allergique à l'amoxicilline

-- INSERTION DES ORDONNANCES (TEST)
INSERT OR IGNORE INTO Ordonnance (idOrdonnance, idPatient, dateOrdonnance, statut) VALUES
(1, 1, '2026-07-10', 'Validée'),
(2, 2, '2026-07-12', 'En attente'),
(3, 3, '2026-07-14', 'Alertée');

INSERT OR IGNORE INTO Ordonnance_Medicament (idOrdonnance, idMedicament, dosage_prescrit, duree_traitement) VALUES
(1, 1, '500mg', 7), -- Karim → Aspirine
(1, 3, '5mg', 30), -- Karim → Coumadine (⚠️ Interaction avec Aspirine)
(2, 2, '500mg', 5), -- Fatima → Doliprane
(3, 4, '400mg', 5); -- Mohammed → Advil

-- Insertion des comptes utilisateurs par défaut
INSERT OR IGNORE INTO Utilisateur (email, mot_de_passe, nom, prenom, role) 
VALUES ('admin@saferx.com', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Admin', 'SafeRx', 'Admin');

INSERT OR IGNORE INTO Utilisateur (email, mot_de_passe, nom, prenom, role) 
VALUES ('pharmacien@saferx.com', 'a2a4b0c2e5d6f7e8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2', 'Pharmacien', 'Demo', 'Pharmacien');