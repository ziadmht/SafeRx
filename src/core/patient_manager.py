# src/core/patient_manager.py
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

class PatientManager:
    """Gestionnaire complet des patients (CRUD)."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
        self.db_path = db_path
    
    def get_all(self) -> List[Dict]:
        """Récupère tous les patients."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idPatient, nss, nom, prenom, dateNaissance, sexe, telephone
            FROM Patient
            ORDER BY nom, prenom
        """)
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                'id': r[0],
                'nss': r[1],
                'nom': r[2],
                'prenom': r[3],
                'dateNaissance': r[4],
                'sexe': r[5],
                'telephone': r[6]
            }
            for r in rows
        ]
    
    def get_by_id(self, patient_id: int) -> Optional[Dict]:
        """Récupère un patient par son ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idPatient, nss, nom, prenom, dateNaissance, sexe, telephone
            FROM Patient
            WHERE idPatient = ?
        """, (patient_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'nss': row[1],
                'nom': row[2],
                'prenom': row[3],
                'dateNaissance': row[4],
                'sexe': row[5],
                'telephone': row[6]
            }
        return None
    
    def get_by_nss(self, nss: str) -> Optional[Dict]:
        """Récupère un patient par son NSS."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idPatient, nss, nom, prenom, dateNaissance, sexe, telephone
            FROM Patient
            WHERE nss = ?
        """, (nss,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'nss': row[1],
                'nom': row[2],
                'prenom': row[3],
                'dateNaissance': row[4],
                'sexe': row[5],
                'telephone': row[6]
            }
        return None

    def get_or_create_by_nss(self, nss: str, patient_data: dict = None) -> dict:
        """
        Récupère un patient par son NSS, ou le crée s'il n'existe pas.
        
        Args:
            nss: Numéro de Sécurité Sociale
            patient_data: Données du patient (nom, prenom, dateNaissance, sexe, telephone)
            
        Returns:
            dict: Patient existant ou nouvellement créé
        """
        if not nss or not nss.strip():
            raise ValueError("Le NSS est obligatoire pour identifier ou créer un patient.")

        patient = self.get_by_nss(nss)
        if patient:
            return patient

        data = patient_data or {}
        try:
            patient_id = self.add(
                nss=nss,
                nom=data.get('nom') or 'Inconnu',
                prenom=data.get('prenom') or 'Inconnu',
                dateNaissance=data.get('dateNaissance'),
                sexe=data.get('sexe') or 'M',
                telephone=data.get('telephone')
            )
            return self.get_by_id(patient_id)
        except sqlite3.IntegrityError:
            # Un autre thread/process a créé le patient entre-temps -> on le récupère
            existing = self.get_by_nss(nss)
            if existing:
                return existing
            raise

    
    def add(self, nss: str, nom: str, prenom: str, dateNaissance: str, sexe: str, telephone: str) -> int:
        """Ajoute un nouveau patient."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # ✅ PRAGMA foreign_keys ON pour les contraintes
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("""
            INSERT INTO Patient (nss, nom, prenom, dateNaissance, sexe, telephone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nss, nom, prenom, dateNaissance, sexe, telephone))
        conn.commit()
        patient_id = cursor.lastrowid
        conn.close()
        return patient_id
    
    def update(self, patient_id: int, nss: str, nom: str, prenom: str, dateNaissance: str, sexe: str, telephone: str) -> bool:
        """Met à jour un patient. Retourne True si succès."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("""
                UPDATE Patient
                SET nss = ?, nom = ?, prenom = ?, dateNaissance = ?, sexe = ?, telephone = ?
                WHERE idPatient = ?
            """, (nss, nom, prenom, dateNaissance, sexe, telephone, patient_id))
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0  # ✅ Retourne True si une ligne a été modifiée
        except Exception as e:
            print(f"Erreur update: {e}")
            return False
    
    def delete(self, patient_id: int) -> bool:
        """Supprime un patient. Retourne True si succès."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("DELETE FROM Patient WHERE idPatient = ?", (patient_id,))
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0  # ✅ Retourne True si une ligne a été supprimée
        except Exception as e:
            print(f"Erreur delete: {e}")
            return False
    
    def get_allergies(self, patient_id: int) -> List[Dict]:
        """Récupère les allergies d'un patient."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.idAllergie, a.idMolecule, m.nom, a.type, a.gravite
            FROM Allergie a
            JOIN Molecule m ON a.idMolecule = m.idMolecule
            WHERE a.idPatient = ?
        """, (patient_id,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                'id': r[0],
                'idMolecule': r[1],
                'nom': r[2],
                'type': r[3],
                'gravite': r[4]
            }
            for r in rows
        ]
    
    def add_allergie(self, patient_id: int, molecule_id: int, type_alle: str, gravite: str) -> bool:
        """Ajoute une allergie à un patient."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("""
                INSERT INTO Allergie (idPatient, idMolecule, type, gravite)
                VALUES (?, ?, ?, ?)
            """, (patient_id, molecule_id, type_alle, gravite))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def delete_allergie(self, patient_id: int, allergie_id: int) -> bool:
        """Supprime une allergie d'un patient."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("DELETE FROM Allergie WHERE idAllergie = ? AND idPatient = ?", (allergie_id, patient_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_molecules(self) -> List[Dict]:
        """Récupère toutes les molécules pour les allergies."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT idMolecule, nom, famille FROM Molecule ORDER BY nom")
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'nom': r[1], 'famille': r[2]} for r in rows]
    
    def get_statistics(self) -> Dict:
        """Récupère les statistiques des patients."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Patient")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT sexe, COUNT(*) FROM Patient GROUP BY sexe")
        sexe_dist = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT COUNT(DISTINCT p.idPatient)
            FROM Patient p
            JOIN Allergie a ON p.idPatient = a.idPatient
        """)
        with_allergies = cursor.fetchone()[0] or 0
        
        conn.close()
        return {
            'total': total,
            'sexe_distribution': sexe_dist,
            'with_allergies': with_allergies,
            'without_allergies': total - with_allergies
        }