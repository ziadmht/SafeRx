# src/database/init_db.py
import sqlite3
import hashlib
from pathlib import Path
import re

def init_database(db_path=None):
    """
    Initialise la base de données avec toutes les tables.
    Si la base existe déjà, ajoute uniquement ce qui manque.
    """
    
    if db_path is None:
        db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
    else:
        db_path = Path(db_path)
    
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ============================================================
    # 1. Lire et exécuter le fichier schema.sql
    # ============================================================
    schema_file = Path(__file__).parent / "schema.sql"
    if schema_file.exists():
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Exécuter le script complet
        try:
            cursor.executescript(sql_script)
            conn.commit()
            print(f"✅ Base de données initialisée : {db_path}")
        except sqlite3.OperationalError as e:
            # Si erreur, exécuter morceau par morceau
            print(f"⚠️ Erreur: {e}")
            print("🔄 Exécution en mode 'safe'...")
            
            # Séparer les instructions SQL
            statements = sql_script.split(';')
            for stmt in statements:
                stmt = stmt.strip()
                if not stmt or stmt.startswith('--'):
                    continue
                try:
                    cursor.execute(stmt)
                    conn.commit()
                except sqlite3.OperationalError as e2:
                    if 'already exists' not in str(e2).lower():
                        print(f"⚠️ Ignoré: {e2}")
    else:
        print(f"❌ Fichier schema.sql introuvable")
        conn.close()
        return
    
    # ============================================================
    # 2. Vérifier que la table Patient a la colonne NSS
    # ============================================================
    try:
        cursor.execute("SELECT nss FROM Patient LIMIT 1")
    except sqlite3.OperationalError:
        # La colonne nss n'existe pas → l'ajouter
        print("🔄 Ajout de la colonne NSS...")
        try:
            # Vérifier si la table Patient_new existe déjà
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Patient'")
            if cursor.fetchone():
                # Sauvegarder les données
                cursor.execute("SELECT idPatient, nom, prenom, dateNaissance, sexe, telephone FROM Patient")
                patients = cursor.fetchall()
                
                # Supprimer les anciennes tables de Patient
                cursor.execute("DROP TABLE IF EXISTS Patient")
                
                # Recréer la table Patient avec NSS
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Patient (
                        idPatient INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom VARCHAR(50) NOT NULL,
                        prenom VARCHAR(50) NOT NULL,
                        dateNaissance DATE,
                        sexe CHAR(1) CHECK (sexe IN ('M', 'F')),
                        telephone VARCHAR(15),
                        nss VARCHAR(15) UNIQUE
                    )
                """)
                
                # Réinsérer les données
                for p in patients:
                    nss_map = {
                        1: '123456789012345',
                        2: '234567890123456',
                        3: '345678901234567',
                        4: '456789012345678',
                        5: '567890123456789'
                    }
                    nss = nss_map.get(p[0], None)
                    cursor.execute("""
                        INSERT INTO Patient (idPatient, nom, prenom, dateNaissance, sexe, telephone, nss)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (p[0], p[1], p[2], p[3], p[4], p[5], nss))
                conn.commit()
                print("✅ Colonne NSS ajoutée avec succès")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'ajout du NSS: {e}")
    
    # ============================================================
    # 3. Vérifier que la table Utilisateur existe
    # ============================================================
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Utilisateur'")
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE Utilisateur (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(100) NOT NULL UNIQUE,
                mot_de_passe VARCHAR(255) NOT NULL,
                nom VARCHAR(50) NOT NULL,
                prenom VARCHAR(50) NOT NULL,
                role VARCHAR(20) CHECK (role IN ('Admin', 'Pharmacien')),
                date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Table Utilisateur créée")
    
    # ============================================================
    # 4. Créer les comptes par défaut si aucun utilisateur
    # ============================================================
    cursor.execute("SELECT COUNT(*) FROM Utilisateur")
    if cursor.fetchone()[0] == 0:
        hashed_admin = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO Utilisateur (email, mot_de_passe, nom, prenom, role)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin@saferx.com", hashed_admin, "Admin", "SafeRx", "Admin"))
        
        hashed_pharma = hashlib.sha256("pharmacien123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO Utilisateur (email, mot_de_passe, nom, prenom, role)
            VALUES (?, ?, ?, ?, ?)
        """, ("pharmacien@saferx.com", hashed_pharma, "Pharmacien", "Demo", "Pharmacien"))
        conn.commit()
        print("✅ Comptes Admin et Pharmacien créés")
    
    conn.close()
    print("✅ Initialisation terminée")
    return str(db_path)

if __name__ == "__main__":
    init_database()