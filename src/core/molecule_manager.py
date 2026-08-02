# src/core/molecule_manager.py
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class MoleculeManager:
    """Gestionnaire complet des molécules (CRUD)."""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
        self.db_path = db_path

    def get_all(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT idMolecule, nom, famille, formule FROM Molecule ORDER BY nom")
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'nom': r[1], 'famille': r[2], 'formule': r[3]} for r in rows]

    def get_by_id(self, molecule_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT idMolecule, nom, famille, formule FROM Molecule WHERE idMolecule = ?", (molecule_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'nom': row[1], 'famille': row[2], 'formule': row[3]}
        return None

    def get_by_name(self, nom: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT idMolecule, nom, famille, formule FROM Molecule WHERE nom = ?", (nom,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'nom': row[1], 'famille': row[2], 'formule': row[3]}
        return None

    def add(self, nom: str, famille: str, formule: str) -> Tuple[bool, str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Molecule (nom, famille, formule) VALUES (?, ?, ?)",
                (nom, famille, formule)
            )
            conn.commit()
            conn.close()
            return True, "Molécule ajoutée."
        except Exception as e:
            return False, str(e)

    def update(self, molecule_id: int, nom: str, famille: str, formule: str) -> Tuple[bool, str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Molecule SET nom = ?, famille = ?, formule = ? WHERE idMolecule = ?",
                (nom, famille, formule, molecule_id)
            )
            conn.commit()
            conn.close()
            return True, "Molécule modifiée."
        except Exception as e:
            return False, str(e)

    def get_dependencies(self, molecule_id: int) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Medicament_Molecule WHERE idMolecule = ?", (molecule_id,))
        nb_medicaments = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM Interaction WHERE idMolecule1 = ? OR idMolecule2 = ?",
            (molecule_id, molecule_id)
        )
        nb_interactions = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Allergie WHERE idMolecule = ?", (molecule_id,))
        nb_allergies = cursor.fetchone()[0]
        conn.close()
        return {
            'medicaments': nb_medicaments,
            'interactions': nb_interactions,
            'allergies': nb_allergies,
            'has_dependencies': (nb_medicaments + nb_interactions + nb_allergies) > 0
        }

    def delete(self, molecule_id: int) -> Tuple[bool, str]:
        deps = self.get_dependencies(molecule_id)
        if deps['has_dependencies']:
            return False, (
                f"Impossible de supprimer : utilisée dans {deps['medicaments']} médicament(s), "
                f"{deps['interactions']} interaction(s) et {deps['allergies']} allergie(s). "
                f"Retirez d'abord ces associations."
            )
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Molecule WHERE idMolecule = ?", (molecule_id,))
            conn.commit()
            conn.close()
            return True, "Molécule supprimée."
        except Exception as e:
            return False, str(e)

    def get_statistics(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Molecule")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT famille, COUNT(*) FROM Molecule GROUP BY famille")
        familles = dict(cursor.fetchall())
        conn.close()
        return {'total': total, 'familles': familles}