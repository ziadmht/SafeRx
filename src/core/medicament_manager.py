# src/core/medicament_manager.py
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class MedicamentManager:
    """Gestionnaire complet des médicaments (CRUD + associations molécules)."""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
        self.db_path = db_path

    def get_all(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idMedicament, nom, codeCIS, forme, dosage, prix
            FROM Medicament ORDER BY nom
        """)
        rows = cursor.fetchall()
        conn.close()
        return [
            {'id': r[0], 'nom': r[1], 'codeCIS': r[2], 'forme': r[3], 'dosage': r[4], 'prix': r[5]}
            for r in rows
        ]

    def get_by_id(self, medicament_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idMedicament, nom, codeCIS, forme, dosage, prix
            FROM Medicament WHERE idMedicament = ?
        """, (medicament_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'nom': row[1], 'codeCIS': row[2], 'forme': row[3], 'dosage': row[4], 'prix': row[5]}
        return None

    def get_by_name(self, nom: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idMedicament, nom, codeCIS, forme, dosage, prix
            FROM Medicament WHERE nom = ?
        """, (nom,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'nom': row[1], 'codeCIS': row[2], 'forme': row[3], 'dosage': row[4], 'prix': row[5]}
        return None

    def add(self, nom: str, codeCIS: str, forme: str, dosage: str, prix: float) -> Tuple[bool, str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Medicament (nom, codeCIS, forme, dosage, prix)
                VALUES (?, ?, ?, ?, ?)
            """, (nom, codeCIS or None, forme, dosage, prix))
            conn.commit()
            conn.close()
            return True, "Médicament ajouté."
        except sqlite3.IntegrityError:
            return False, f"Le code CIS '{codeCIS}' existe déjà."
        except Exception as e:
            return False, str(e)

    def update(self, medicament_id: int, nom: str, codeCIS: str, forme: str, dosage: str, prix: float) -> Tuple[bool, str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Medicament
                SET nom = ?, codeCIS = ?, forme = ?, dosage = ?, prix = ?
                WHERE idMedicament = ?
            """, (nom, codeCIS or None, forme, dosage, prix, medicament_id))
            conn.commit()
            conn.close()
            return True, "Médicament modifié."
        except sqlite3.IntegrityError:
            return False, f"Le code CIS '{codeCIS}' existe déjà."
        except Exception as e:
            return False, str(e)

    def get_dependencies(self, medicament_id: int) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Medicament_Molecule WHERE idMedicament = ?", (medicament_id,))
        nb_molecules = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Ordonnance_Medicament WHERE idMedicament = ?", (medicament_id,))
        nb_ordonnances = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Analyse_Medicament WHERE idMedicament = ?", (medicament_id,))
        nb_analyses = cursor.fetchone()[0]
        conn.close()
        return {
            'molecules': nb_molecules,
            'ordonnances': nb_ordonnances,
            'analyses': nb_analyses,
            'has_dependencies': (nb_ordonnances + nb_analyses) > 0
        }

    def delete(self, medicament_id: int) -> Tuple[bool, str]:
        deps = self.get_dependencies(medicament_id)
        if deps['has_dependencies']:
            return False, (
                f"Impossible de supprimer : ce médicament est référencé dans "
                f"{deps['ordonnances']} ordonnance(s) et {deps['analyses']} analyse(s)."
            )
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Medicament_Molecule WHERE idMedicament = ?", (medicament_id,))
            cursor.execute("DELETE FROM Medicament WHERE idMedicament = ?", (medicament_id,))
            conn.commit()
            conn.close()
            return True, "Médicament supprimé."
        except Exception as e:
            return False, str(e)

    def get_molecules(self, medicament_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.idMolecule, m.nom, m.famille
            FROM Medicament_Molecule mm
            JOIN Molecule m ON mm.idMolecule = m.idMolecule
            WHERE mm.idMedicament = ?
        """, (medicament_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'nom': r[1], 'famille': r[2]} for r in rows]

    def add_molecule(self, medicament_id: int, molecule_id: int) -> Tuple[bool, str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO Medicament_Molecule (idMedicament, idMolecule)
                VALUES (?, ?)
            """, (medicament_id, molecule_id))
            conn.commit()
            conn.close()
            return True, "Association ajoutée."
        except Exception as e:
            return False, str(e)

    def remove_molecule(self, medicament_id: int, molecule_id: int) -> Tuple[bool, str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM Medicament_Molecule
                WHERE idMedicament = ? AND idMolecule = ?
            """, (medicament_id, molecule_id))
            conn.commit()
            conn.close()
            return True, "Association supprimée."
        except Exception as e:
            return False, str(e)

    def get_statistics(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Medicament")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT idMedicament) FROM Medicament_Molecule")
        with_molecules = cursor.fetchone()[0] or 0
        conn.close()
        return {
            'total': total,
            'with_molecules': with_molecules,
            'without_molecules': total - with_molecules
        }