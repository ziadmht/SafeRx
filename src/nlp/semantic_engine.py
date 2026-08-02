# src/nlp/semantic_engine.py
import numpy as np
from pathlib import Path
import sqlite3
import pickle
import time
from typing import List, Tuple, Optional, Dict, Any

class SemanticEngine:
    """
    Moteur sémantique complet pour SafeRx.
    Combine les embeddings, la base de données et les interactions.
    """
    
    def __init__(self, db_path=None, auto_create=True):
        """
        Initialise le moteur sémantique.
        
        Args:
            db_path: Chemin vers la base de données SQLite
            auto_create: Créer automatiquement la BDD si elle n'existe pas
        """
        self._load_time = time.time()
        
        # ===== POINT 1 : Fallback si sentence_transformers absent =====
        try:
            from src.nlp.embedding_engine import EmbeddingEngine
            self.embedding_engine = EmbeddingEngine()
            self._nlp_available = True
        except ImportError:
            print("⚠️ sentence_transformers non disponible, fallback sur des vecteurs simples")
            self._nlp_available = False
            self.embedding_engine = None
        
        # ===== POINT 5 : Création automatique de la BDD =====
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
        self.db_path = Path(db_path)
        
        if auto_create and not self.db_path.exists():
            from src.database.init_db import init_database
            print(f"🔄 Base de données absente, création automatique...")
            init_database(self.db_path)
        
        # ===== POINT 4 : Cache des alternatives =====
        self._alternatives_cache = {}
        self._max_alt_cache_size = 100
        
        # ===== POINT 3 : Préchargement des molécules =====
        self._load_data()
        self._preload_common_molecules()
        
        print(f"✅ Moteur sémantique initialisé")
        print(f"   📊 {len(self.molecules)} molécules chargées")
        print(f"   💊 {len(self.medicaments)} médicaments chargés")
        print(f"   🔗 {len(self.interactions)} interactions chargées")
        print(f"   🧠 NLP: {'✅ Disponible' if self._nlp_available else '⚠️ Fallback'}")
    
    # ===== POINT 3 : Préchargement =====
    def _preload_common_molecules(self):
        """Précharge les molécules fréquentes pour accélérer."""
        common = ["Aspirine", "Paracétamol", "Ibuprofène", "Warfarine", 
                  "Amoxicilline", "Pénicilline", "Diclofénac", "Oméprazole"]
        if self._nlp_available and self.embedding_engine:
            for mol in common:
                self.get_molecule_embedding(mol)
    
    def _load_data(self):
        """Charge toutes les données depuis la base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Charger les molécules
            cursor.execute("""
                SELECT idMolecule, nom, famille 
                FROM Molecule
            """)
            self.molecules = cursor.fetchall()
            self.molecule_names = [m[1] for m in self.molecules]
            
            # Charger les médicaments
            cursor.execute("""
                SELECT idMedicament, nom 
                FROM Medicament
            """)
            self.medicaments = cursor.fetchall()
            self.medicament_names = [m[1] for m in self.medicaments]
            
            # Charger les relations
            cursor.execute("""
                SELECT idMedicament, idMolecule 
                FROM Medicament_Molecule
            """)
            self.med_mol_relations = cursor.fetchall()
            
            # Charger les interactions
            cursor.execute("""
                SELECT idMolecule1, idMolecule2, niveau, description, recommandation 
                FROM Interaction
            """)
            self.interactions = cursor.fetchall()
            
            # Charger les allergies
            cursor.execute("""
                SELECT idPatient, idMolecule, type, gravite 
                FROM Allergie
            """)
            self.allergies = cursor.fetchall()
            
            conn.close()
            
        except sqlite3.OperationalError as e:
            print(f"⚠️ Erreur BDD: {e}")
            self.molecules = []
            self.molecule_names = []
            self.medicaments = []
            self.medicament_names = []
            self.med_mol_relations = []
            self.interactions = []
            self.allergies = []
        
        self._build_indexes()
    
    def _build_indexes(self):
        """Construit des index pour un accès rapide"""
        self.molecule_by_name = {m[1].lower(): m[0] for m in self.molecules}
        self.molecule_by_id = {m[0]: {'nom': m[1], 'famille': m[2]} for m in self.molecules}
        self.medicament_by_name = {m[1].lower(): m[0] for m in self.medicaments}
        self.medicament_by_id = {m[0]: {'nom': m[1]} for m in self.medicaments}
        
        self.medicament_molecules = {}
        for med_id, mol_id in self.med_mol_relations:
            self.medicament_molecules.setdefault(med_id, []).append(mol_id)
        
        self.interactions_by_molecule = {}
        for mol1, mol2, niveau, desc, reco in self.interactions:
            self.interactions_by_molecule.setdefault(mol1, []).append((mol2, niveau, desc, reco))
            self.interactions_by_molecule.setdefault(mol2, []).append((mol1, niveau, desc, reco))
        
        self.allergies_by_patient = {}
        for patient_id, mol_id, type_alle, gravite in self.allergies:
            self.allergies_by_patient.setdefault(patient_id, []).append((mol_id, type_alle, gravite))
    
    def get_medicament_molecules(self, medicament_nom):
        """Récupère les molécules d'un médicament."""
        med_id = self.medicament_by_name.get(medicament_nom.lower())
        if not med_id:
            return []
        mol_ids = self.medicament_molecules.get(med_id, [])
        return [self.molecule_by_id.get(mol_id, {}) for mol_id in mol_ids if mol_id in self.molecule_by_id]
    
    def get_molecule_embedding(self, molecule_nom):
        """Retourne l'embedding d'une molécule."""
        if self._nlp_available and self.embedding_engine:
            return self.embedding_engine.encode(molecule_nom)
        # Fallback : vecteur basé sur les caractères
        import hashlib
        h = hashlib.sha256(molecule_nom.lower().encode()).hexdigest()
        return np.array([int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)], dtype=np.float32)
    
    def get_similar_molecules(self, text, threshold=0.6):
        """Trouve les molécules similaires à un texte donné."""
        if not self._nlp_available or not self.embedding_engine:
            # Recherche simple par mot-clé
            results = []
            for nom in self.molecule_names:
                if text.lower() in nom.lower():
                    results.append((nom, 0.8, self.molecule_by_name.get(nom.lower())))
                elif any(text.lower() in part for part in nom.lower().split()):
                    results.append((nom, 0.5, self.molecule_by_name.get(nom.lower())))
            return results[:10]
        
        results = self.embedding_engine.find_similar(text, self.molecule_names, threshold=threshold)
        return [(nom, sim, self.molecule_by_name.get(nom.lower())) for nom, sim in results if nom.lower() in self.molecule_by_name]
    
    def get_patient_allergies(self, patient_id):
        """Récupère toutes les allergies d'un patient."""
        allergies = self.allergies_by_patient.get(patient_id, [])
        result = []
        for mol_id, type_alle, gravite in allergies:
            mol = self.molecule_by_id.get(mol_id, {})
            if mol:
                result.append((mol_id, mol.get('nom', 'Inconnu'), type_alle, gravite))
        return result
    
    def detect_interactions(self, medicament_ids):
        """Détecte les interactions entre une liste de médicaments."""
        all_molecules = []
        for med_id in medicament_ids:
            all_molecules.extend(self.medicament_molecules.get(med_id, []))
        all_molecules = list(set(all_molecules))
        
        detected = []
        for i, mol1 in enumerate(all_molecules):
            for mol2 in all_molecules[i+1:]:
                for mol2_interact, niveau, desc, reco in self.interactions_by_molecule.get(mol1, []):
                    if mol2_interact == mol2:
                        detected.append((mol1, mol2, niveau, desc, reco))
        return detected
    
    def check_allergies(self, patient_id, medicament_ids):
        """Vérifie les allergies d'un patient par rapport aux médicaments."""
        patient_allergies = self.allergies_by_patient.get(patient_id, [])
        patient_mol_ids = [a[0] for a in patient_allergies]
        
        med_molecules = []
        for med_id in medicament_ids:
            med_molecules.extend(self.medicament_molecules.get(med_id, []))
        med_molecules = list(set(med_molecules))
        
        detected = []
        for mol_id in med_molecules:
            if mol_id in patient_mol_ids:
                for a in patient_allergies:
                    if a[0] == mol_id:
                        mol = self.molecule_by_id.get(mol_id, {})
                        detected.append((mol_id, mol.get('nom', 'Inconnu'), a[1], a[2]))
                        break
        return detected
    
    # ===== POINT 4 : Cache des alternatives =====
    def get_alternatives(self, medicament_id, threshold=0.6):
        """Trouve des alternatives à un médicament avec cache."""
        cache_key = f"{medicament_id}_{threshold}"
        
        # Vérifier le cache
        if cache_key in self._alternatives_cache:
            return self._alternatives_cache[cache_key]
        
        if not self._nlp_available or not self.embedding_engine:
            return []
        
        mols = self.medicament_molecules.get(medicament_id, [])
        if not mols:
            return []
        
        med_nom = self.medicament_by_id.get(medicament_id, {}).get('nom')
        if not med_nom:
            return []
        
        # Recherche d'alternatives
        alternatives = []
        for mol_id in mols:
            mol = self.molecule_by_id.get(mol_id, {})
            if mol:
                results = self.embedding_engine.find_similar(
                    mol.get('nom', ''), 
                    self.medicament_names, 
                    threshold=threshold
                )
                for nom, sim in results:
                    if nom.lower() != med_nom.lower():
                        alternatives.append((nom, sim))
        
        # Trier et éliminer les doublons
        seen = set()
        unique_alt = []
        for nom, sim in sorted(alternatives, key=lambda x: x[1], reverse=True):
            if nom not in seen:
                seen.add(nom)
                unique_alt.append((nom, sim))
        
        result = unique_alt[:10]
        
        # Mettre en cache
        if len(self._alternatives_cache) >= self._max_alt_cache_size:
            first_key = next(iter(self._alternatives_cache))
            del self._alternatives_cache[first_key]
        self._alternatives_cache[cache_key] = result
        
        return result
    
    def get_molecule_id_by_name(self, name):
        """Retourne l'ID d'une molécule par son nom."""
        return self.molecule_by_name.get(name.lower())
    
    def get_patient_by_id(self, patient_id):
        """Récupère les informations d'un patient."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT idPatient, nom, prenom, dateNaissance, sexe, telephone
                FROM Patient
                WHERE idPatient = ?
            """, (patient_id,))
            patient = cursor.fetchone()
            conn.close()
            return patient
        except:
            return None
    
    # ===== POINT 2 : Métriques de performance =====
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retourne des métriques de performance."""
        load_time = time.time() - self._load_time
        
        metrics = {
            'load_time_seconds': round(load_time, 2),
            'nlp_available': self._nlp_available,
            'molecules_count': len(self.molecules),
            'medicaments_count': len(self.medicaments),
            'interactions_count': len(self.interactions),
            'alternatives_cache_size': len(self._alternatives_cache),
        }
        
        # Ajouter les métriques du moteur d'embeddings si disponible
        if self._nlp_available and self.embedding_engine:
            try:
                cache_stats = self.embedding_engine.get_cache_stats()
                metrics['cache_hit_rate'] = cache_stats.get('hit_rate', 'N/A')
                metrics['cache_size'] = cache_stats.get('persistent_cache_size', 0)
            except:
                pass
        
        return metrics
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache."""
        stats = {
            'alternatives_cache_size': len(self._alternatives_cache),
            'max_alt_cache_size': self._max_alt_cache_size,
        }
        
        if self._nlp_available and self.embedding_engine:
            try:
                cache_stats = self.embedding_engine.get_cache_stats()
                stats.update(cache_stats)
            except:
                pass
        
        return stats
    
    def clear_cache(self):
        """Vide tous les caches."""
        self._alternatives_cache = {}
        if self._nlp_available and self.embedding_engine:
            try:
                self.embedding_engine.clear_cache()
            except:
                pass
        print("🗑️ Cache vidé")