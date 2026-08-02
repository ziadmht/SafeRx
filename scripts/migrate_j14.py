# scripts/migrate_j14.py
import sqlite3
from pathlib import Path
import sys

# Ajouter le dossier parent au path
sys.path.append(str(Path(__file__).parent.parent))

DB_PATH = Path(__file__).parent.parent / "data" / "safeRx.db"

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def main():
    print("[Migration J14] Démarrage...")
    
    if not DB_PATH.exists():
        print(f"❌ Base de données non trouvée : {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ============================================================
    # 1. Colonnes de validation sur Analyse
    # ============================================================
    if not column_exists(cursor, "Analyse", "statut_validation"):
        cursor.execute("ALTER TABLE Analyse ADD COLUMN statut_validation VARCHAR(20) DEFAULT 'En attente'")
        print("✅ Colonne statut_validation ajoutée")
    else:
        print("ℹ️ Colonne statut_validation existe déjà")
    
    if not column_exists(cursor, "Analyse", "date_validation"):
        cursor.execute("ALTER TABLE Analyse ADD COLUMN date_validation DATETIME")
        print("✅ Colonne date_validation ajoutée")
    else:
        print("ℹ️ Colonne date_validation existe déjà")
    
    if not column_exists(cursor, "Analyse", "idFacture"):
        cursor.execute("ALTER TABLE Analyse ADD COLUMN idFacture INTEGER")
        print("✅ Colonne idFacture ajoutée")
    else:
        print("ℹ️ Colonne idFacture existe déjà")
    
    # ============================================================
    # 2. Rétro-compatibilité
    # ============================================================
    cursor.execute("""
        UPDATE Analyse SET statut_validation = 'Validée'
        WHERE statut_validation IS NULL AND statut IN ('Sécurisée', 'Alerte')
    """)
    cursor.execute("""
        UPDATE Analyse SET statut_validation = 'Annulée'
        WHERE statut_validation IS NULL AND statut = 'Annulée'
    """)
    print("✅ Analyses existantes mises à jour")
    
    # ============================================================
    # 3. Tables Facture / LigneFacture
    # ============================================================
    cursor.execute("""
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
        )
    """)
    print("✅ Table Facture créée/vérifiée")
    
    cursor.execute("""
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
        )
    """)
    print("✅ Table LigneFacture créée/vérifiée")
    
    conn.commit()
    conn.close()
    
    print("✅ Migration J14 terminée avec succès !")
    print(f"📁 Base : {DB_PATH}")

if __name__ == "__main__":
    main()