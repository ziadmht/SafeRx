# src/core/facture_manager.py
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class FactureManager:
    """Gestionnaire complet des factures - Modèle intégré."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
        self.db_path = db_path
        self._create_tables_if_needed()
    
    def _create_tables_if_needed(self):
        """Crée les tables de facturation si elles n'existent pas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        
        conn.commit()
        conn.close()
    
    def generer_facture(self, analyse_id: int, patient_id: int, medicaments: List[str], db) -> Tuple[bool, str, Dict]:
        """
        Génère une facture à partir d'une analyse validée.
        ✅ Numéro basé sur analyse_id (garanti unique)
        ✅ Prix lus depuis la base
        ✅ Ligne ignorée si médicament non trouvé (avec warning)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ✅ Numéro basé sur analyse_id (unique grâce à UNIQUE(idAnalyse))
            numero = f"FAC-{datetime.now().strftime('%Y%m%d')}-{analyse_id:06d}"
            
            # Calculer le montant total
            total = 0.0
            lignes = []
            medicaments_introuvables = []
            
            for nom in medicaments:
                rows = db.execute_query(
                    "SELECT idMedicament, nom, prix FROM Medicament WHERE LOWER(nom) = LOWER(?)",
                    (nom.strip(),)
                )
                if rows:
                    med_id, med_nom, prix = rows[0]
                    prix = prix or 0.0
                    total += prix
                    lignes.append({
                        'idMedicament': med_id,
                        'nom_medicament': med_nom,
                        'prix_unitaire': prix
                    })
                else:
                    medicaments_introuvables.append(nom)
            
            if medicaments_introuvables:
                print(f"[Facture] ⚠️ Médicaments sans prix : {medicaments_introuvables}")
            
            # Insérer la facture
            cursor.execute("""
                INSERT INTO Facture (idAnalyse, idPatient, numero, montant_total, statut)
                VALUES (?, ?, ?, ?, ?)
            """, (analyse_id, patient_id, numero, round(total, 2), 'En attente'))
            
            facture_id = cursor.lastrowid
            
            # Insérer les lignes
            for ligne in lignes:
                cursor.execute("""
                    INSERT INTO LigneFacture (idFacture, idMedicament, nom_medicament, 
                                            quantite, prix_unitaire, montant_ligne)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    facture_id,
                    ligne['idMedicament'],
                    ligne['nom_medicament'],
                    1,
                    ligne['prix_unitaire'],
                    ligne['prix_unitaire']
                ))
            
            # Mettre à jour l'analyse
            cursor.execute("""
                UPDATE Analyse 
                SET statut_validation = 'Validée', 
                    date_validation = CURRENT_TIMESTAMP, 
                    idFacture = ?
                WHERE idAnalyse = ?
            """, (facture_id, analyse_id))
            
            conn.commit()
            conn.close()
            
            facture = self.get_by_id(facture_id)
            return True, "Facture générée avec succès", facture
            
        except sqlite3.IntegrityError as e:
            return False, f"Erreur d'intégrité : {e}", {}
        except Exception as e:
            return False, str(e), {}
    
    def get_by_id(self, facture_id: int) -> Optional[Dict]:
        """Récupère une facture avec ses lignes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT f.idFacture, f.numero, f.date_emission, f.montant_total, f.statut,
                   f.reference_paiement, f.date_paiement,
                   p.nom, p.prenom
            FROM Facture f
            JOIN Patient p ON f.idPatient = p.idPatient
            WHERE f.idFacture = ?
        """, (facture_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        facture = {
            'id': row[0],
            'numero': row[1],
            'date_emission': row[2],
            'montant_total': row[3],
            'statut': row[4],
            'reference_paiement': row[5],
            'date_paiement': row[6],
            'patient': f"{row[7]} {row[8]}",
            'lignes': []
        }
        
        cursor.execute("""
            SELECT nom_medicament, quantite, prix_unitaire, montant_ligne
            FROM LigneFacture
            WHERE idFacture = ?
        """, (facture_id,))
        
        for ligne in cursor.fetchall():
            facture['lignes'].append({
                'nom_medicament': ligne[0],
                'quantite': ligne[1],
                'prix_unitaire': ligne[2],
                'montant_ligne': ligne[3]
            })
        
        conn.close()
        return facture
    
    def payer(self, facture_id: int, reference_paiement: str) -> Tuple[bool, str]:
        """Marque une facture comme payée."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE Facture 
                SET statut = 'Payée', 
                    reference_paiement = ?, 
                    date_paiement = CURRENT_TIMESTAMP
                WHERE idFacture = ? AND statut = 'En attente'
            """, (reference_paiement, facture_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return False, "Facture non trouvée ou déjà payée"
            
            conn.commit()
            conn.close()
            return True, "Paiement enregistré avec succès"
            
        except Exception as e:
            return False, str(e)
    
    def get_statistiques(self) -> Dict:
        """Retourne les statistiques de facturation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Facture")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT statut, COUNT(*) FROM Facture GROUP BY statut")
        par_statut = dict(cursor.fetchall())
        
        cursor.execute("SELECT SUM(montant_total) FROM Facture WHERE statut = 'Payée'")
        total_paye = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(montant_total) FROM Facture WHERE statut = 'En attente'")
        total_attente = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total': total,
            'par_statut': par_statut,
            'total_paye': total_paye,
            'total_attente': total_attente
        }