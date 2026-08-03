import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "safeRx.db"


def migrer_facture():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=OFF")
    cursor = conn.cursor()

    print("Migration de la table Facture...")

    cursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Facture'")
    row = cursor.fetchone()
    ancien_seq = row[0] if row else 0

    cursor.execute("""
        CREATE TABLE Facture_new (
            idFacture INTEGER PRIMARY KEY AUTOINCREMENT,
            idAnalyse INTEGER NOT NULL UNIQUE,
            idPatient INTEGER NOT NULL,
            numero VARCHAR(50) NOT NULL UNIQUE,
            date_emission DATETIME DEFAULT CURRENT_TIMESTAMP,
            montant_total DECIMAL(10,2) NOT NULL,
            statut VARCHAR(20),
            reference_paiement VARCHAR(50),
            date_paiement DATETIME,
            FOREIGN KEY (idAnalyse) REFERENCES Analyse(idAnalyse),
            FOREIGN KEY (idPatient) REFERENCES Patient(idPatient)
        )
    """)

    cursor.execute("""
        INSERT INTO Facture_new (
            idFacture, idAnalyse, idPatient, numero, date_emission,
            montant_total, statut, reference_paiement, date_paiement
        )
        SELECT
            idFacture, idAnalyse, idPatient, numero, date_emission,
            montant_total, statut, reference_paiement, date_paiement
        FROM Facture
    """)

    cursor.execute("DROP TABLE Facture")
    cursor.execute("ALTER TABLE Facture_new RENAME TO Facture")

    cursor.execute("SELECT COUNT(*) FROM sqlite_sequence WHERE name = 'Facture'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('Facture', ?)", (ancien_seq,))
    else:
        cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'Facture'", (ancien_seq,))

    print("Contrainte CHECK supprimée de Facture.")

    cursor.execute("UPDATE Facture SET statut = 'EN_ATTENTE' WHERE statut = 'En attente'")
    print(f"  {cursor.rowcount} -> EN_ATTENTE")
    cursor.execute("UPDATE Facture SET statut = 'PAYEE' WHERE statut = 'Payée'")
    print(f"  {cursor.rowcount} -> PAYEE")
    cursor.execute("UPDATE Facture SET statut = 'ANNULEE' WHERE statut = 'Annulée'")
    print(f"  {cursor.rowcount} -> ANNULEE")

    conn.commit()
    conn.execute("PRAGMA foreign_keys=ON")
    conn.close()
    print("Migration Facture terminée.")


if __name__ == "__main__":
    migrer_facture()
