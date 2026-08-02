# scripts/migrate_constants.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "safeRx.db"


def migrer_constants():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=OFF")
    cursor = conn.cursor()

    print("🔄 Migration des statuts et niveaux...")

    # ============================================================
    # 1. Migration de la table Analyse
    # ============================================================
    
    cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Analyse'")
    row = cursor.fetchone()
    ancien_seq_analyse = row[0] if row else 0

    cursor.execute("""
        CREATE TABLE Analyse_new (
            idAnalyse INTEGER PRIMARY KEY AUTOINCREMENT,
            idPatient INTEGER NOT NULL,
            dateAnalyse DATETIME DEFAULT CURRENT_TIMESTAMP,
            statut VARCHAR(20),
            nb_alertes INTEGER DEFAULT 0,
            nb_interactions INTEGER DEFAULT 0,
            nb_allergies INTEGER DEFAULT 0,
            statut_validation VARCHAR(20) DEFAULT 'En attente',
            date_validation DATETIME,
            idFacture INTEGER,
            FOREIGN KEY (idPatient) REFERENCES Patient(idPatient)
        )
    """)

    cursor.execute("""
        INSERT INTO Analyse_new (
            idAnalyse, idPatient, dateAnalyse, statut, nb_alertes,
            nb_interactions, nb_allergies, statut_validation, date_validation, idFacture
        )
        SELECT
            idAnalyse, idPatient, dateAnalyse, statut, nb_alertes,
            nb_interactions, nb_allergies, statut_validation, date_validation, idFacture
        FROM Analyse
    """)

    cursor.execute("DROP TABLE Analyse")
    cursor.execute("ALTER TABLE Analyse_new RENAME TO Analyse")

    cursor.execute("SELECT COUNT(*) FROM sqlite_sequence WHERE name = 'Analyse'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('Analyse', ?)", (ancien_seq_analyse,))
    else:
        cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'Analyse'", (ancien_seq_analyse,))

    print("✅ Table Analyse migree")

    cursor.execute("UPDATE Analyse SET statut = 'SECURISEE' WHERE statut = 'Sécurisée'")
    print(f"  {cursor.rowcount} -> SECURISEE")

    cursor.execute("UPDATE Analyse SET statut = 'ALERTE' WHERE statut = 'Alerte'")
    print(f"  {cursor.rowcount} -> ALERTE")

    cursor.execute("UPDATE Analyse SET statut = 'ANNULEE' WHERE statut = 'Annulée'")
    print(f"  {cursor.rowcount} -> ANNULEE (statut)")

    cursor.execute("UPDATE Analyse SET statut_validation = 'EN_ATTENTE' WHERE statut_validation = 'En attente'")
    print(f"  {cursor.rowcount} -> EN_ATTENTE")

    cursor.execute("UPDATE Analyse SET statut_validation = 'VALIDEE' WHERE statut_validation = 'Validée'")
    print(f"  {cursor.rowcount} -> VALIDEE")

    cursor.execute("UPDATE Analyse SET statut_validation = 'ANNULEE' WHERE statut_validation = 'Annulée'")
    print(f"  {cursor.rowcount} -> ANNULEE (statut_validation)")

    # ============================================================
    # 2. Migration de la table Alerte_Historique
    # ============================================================
    
    print("\n🔄 Migration des alertes...")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Alerte_Historique'")
    if cursor.fetchone():
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Alerte_Historique'")
        row = cursor.fetchone()
        ancien_seq_alerte = row[0] if row else 0

        cursor.execute("""
            CREATE TABLE Alerte_Historique_new (
                idAlerte INTEGER PRIMARY KEY AUTOINCREMENT,
                idAnalyse INTEGER NOT NULL,
                type_alerte VARCHAR(20),
                niveau VARCHAR(20),
                message TEXT,
                description TEXT,
                recommandation TEXT,
                medicaments_concernee TEXT,
                FOREIGN KEY (idAnalyse) REFERENCES Analyse(idAnalyse)
            )
        """)

        cursor.execute("""
            INSERT INTO Alerte_Historique_new (
                idAlerte, idAnalyse, type_alerte, niveau, message,
                description, recommandation, medicaments_concernee
            )
            SELECT
                idAlerte, idAnalyse, type_alerte, niveau, message,
                description, recommandation, medicaments_concernee
            FROM Alerte_Historique
        """)

        cursor.execute("DROP TABLE Alerte_Historique")
        cursor.execute("ALTER TABLE Alerte_Historique_new RENAME TO Alerte_Historique")

        cursor.execute("SELECT COUNT(*) FROM sqlite_sequence WHERE name = 'Alerte_Historique'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('Alerte_Historique', ?)", (ancien_seq_alerte,))
        else:
            cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'Alerte_Historique'", (ancien_seq_alerte,))

        print("✅ Table Alerte_Historique migree")

        cursor.execute("UPDATE Alerte_Historique SET niveau = 'ELEVE' WHERE niveau = 'Élevé'")
        print(f"  {cursor.rowcount} -> ELEVE")

        cursor.execute("UPDATE Alerte_Historique SET niveau = 'MOYEN' WHERE niveau = 'Moyen'")
        print(f"  {cursor.rowcount} -> MOYEN")

        cursor.execute("UPDATE Alerte_Historique SET niveau = 'FAIBLE' WHERE niveau = 'Faible'")
        print(f"  {cursor.rowcount} -> FAIBLE")
    else:
        print("  ⚠️ Table Alerte_Historique non trouvee")

    # ============================================================
    # ✅ NOUVEAU : 3. Migration de la table Interaction
    # ============================================================
    
    print("\n🔄 Migration de la table Interaction...")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Interaction'")
    if cursor.fetchone():
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Interaction'")
        row = cursor.fetchone()
        ancien_seq_interaction = row[0] if row else 0

        cursor.execute("""
            CREATE TABLE Interaction_new (
                idInteraction INTEGER PRIMARY KEY AUTOINCREMENT,
                idMolecule1 INTEGER NOT NULL,
                idMolecule2 INTEGER NOT NULL,
                niveau VARCHAR(10),
                description TEXT,
                recommandation TEXT,
                FOREIGN KEY (idMolecule1) REFERENCES Molecule(idMolecule),
                FOREIGN KEY (idMolecule2) REFERENCES Molecule(idMolecule)
            )
        """)

        cursor.execute("""
            INSERT INTO Interaction_new (idInteraction, idMolecule1, idMolecule2, niveau, description, recommandation)
            SELECT idInteraction, idMolecule1, idMolecule2, niveau, description, recommandation
            FROM Interaction
        """)

        cursor.execute("DROP TABLE Interaction")
        cursor.execute("ALTER TABLE Interaction_new RENAME TO Interaction")

        cursor.execute("SELECT COUNT(*) FROM sqlite_sequence WHERE name = 'Interaction'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('Interaction', ?)", (ancien_seq_interaction,))
        else:
            cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'Interaction'", (ancien_seq_interaction,))

        print("✅ Table Interaction migree")

        cursor.execute("UPDATE Interaction SET niveau = 'ELEVE' WHERE niveau = 'Élevé'")
        print(f"  {cursor.rowcount} -> ELEVE (Interaction)")

        cursor.execute("UPDATE Interaction SET niveau = 'MOYEN' WHERE niveau = 'Moyen'")
        print(f"  {cursor.rowcount} -> MOYEN (Interaction)")

        cursor.execute("UPDATE Interaction SET niveau = 'FAIBLE' WHERE niveau = 'Faible'")
        print(f"  {cursor.rowcount} -> FAIBLE (Interaction)")
    else:
        print("  ⚠️ Table Interaction non trouvee")

    conn.commit()
    conn.execute("PRAGMA foreign_keys=ON")
    conn.close()
    print("\n✅ Migration terminee !")


if __name__ == "__main__":
    migrer_constants()