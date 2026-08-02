import sqlite3
from pathlib import Path


def init_database(db_path=None):
    """Initialise la base de données SQLite avec toutes les tables et données de test."""

    if db_path is None:
        db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
    else:
        db_path = Path(db_path)

    # Créer le dossier data si nécessaire
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connexion à la base
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lecture du fichier SQL
    sql_file = Path(__file__).parent / "schema.sql"
    
    if sql_file.exists():
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Exécution du script SQL
        cursor.executescript(sql_script)
        conn.commit()
        print("[OK] Base de donnees creee avec succes !")
        print(f"Fichier : {db_path}")
    else:
        print("[ERROR] Fichier schema.sql introuvable")
    
    conn.close()
    
    return str(db_path)

if __name__ == "__main__":
    init_database()
