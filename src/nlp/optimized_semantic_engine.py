import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.nlp.optimized_embedding_engine import OptimizedEmbeddingEngine


class OptimizedSemanticEngine:
    """Moteur sémantique optimisé avec cache avancé et index SQL."""

    def __init__(self, db_path=None, precompute: bool = True):
        start = time.time()
        self.embedding_engine = OptimizedEmbeddingEngine()

        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / 'data' / 'safeRx.db'
        self.db_path = db_path

        self._load_data_with_index()

        if precompute and self.molecules:
            self.embedding_engine.precompute_for_database(self.molecule_names)

        self.interactions = []
        for molecule_id, interactions in self.interactions_by_molecule.items():
            for target_id, niveau, desc, reco in interactions:
                self.interactions.append((molecule_id, target_id, niveau, desc, reco))

        elapsed = time.time() - start
        print(f"✅ Moteur sémantique optimisé initialisé en {elapsed:.2f}s")
        print(f"   📊 {len(self.molecules)} molécules")
        print(f"   💊 {len(self.medicaments)} médicaments")
        print(f"   🔗 {len(self.interactions)} interactions")
        print(f"   💾 Cache: {self.embedding_engine.get_cache_stats()['persistent_cache_size']} entrées")

    def _load_data_with_index(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.executescript("""
            CREATE INDEX IF NOT EXISTS idx_allergie_patient ON Allergie(idPatient);
            CREATE INDEX IF NOT EXISTS idx_interaction_molecule ON Interaction(idMolecule1, idMolecule2);
            CREATE INDEX IF NOT EXISTS idx_medicament_molecule ON Medicament_Molecule(idMedicament, idMolecule);
            CREATE INDEX IF NOT EXISTS idx_analyse_patient ON Analyse(idPatient);
            CREATE INDEX IF NOT EXISTS idx_ordonnance_patient ON Ordonnance(idPatient);
        """)
        conn.commit()

        cursor.execute("SELECT idMolecule, nom, famille FROM Molecule ORDER BY nom")
        self.molecules = cursor.fetchall()
        self.molecule_names = [m[1] for m in self.molecules]
        self.molecule_by_name = {m[1].lower(): m[0] for m in self.molecules}
        self.molecule_by_id = {m[0]: {'nom': m[1], 'famille': m[2]} for m in self.molecules}

        cursor.execute("SELECT idMedicament, nom, codeCIS, forme, dosage, prix FROM Medicament ORDER BY nom")
        self.medicaments = cursor.fetchall()
        self.medicament_names = [m[1] for m in self.medicaments]
        self.medicament_by_name = {m[1].lower(): m[0] for m in self.medicaments}
        self.medicament_by_id = {m[0]: {'nom': m[1], 'codeCIS': m[2]} for m in self.medicaments}

        cursor.execute("SELECT idMedicament, idMolecule FROM Medicament_Molecule")
        self.med_mol_relations = {}
        for med_id, mol_id in cursor.fetchall():
            self.med_mol_relations.setdefault(med_id, []).append(mol_id)

        cursor.execute("SELECT idMolecule1, idMolecule2, niveau, description, recommandation FROM Interaction")
        self.interactions_by_molecule = {}
        for mol1, mol2, niveau, desc, reco in cursor.fetchall():
            self.interactions_by_molecule.setdefault(mol1, []).append((mol2, niveau, desc, reco))
            self.interactions_by_molecule.setdefault(mol2, []).append((mol1, niveau, desc, reco))

        cursor.execute("SELECT idPatient, idMolecule, type, gravite FROM Allergie")
        self.allergies_by_patient = {}
        for patient_id, mol_id, type_alle, gravite in cursor.fetchall():
            self.allergies_by_patient.setdefault(patient_id, []).append((mol_id, type_alle, gravite))

        conn.close()

    def get_medicament_molecules(self, medicament_nom: str):
        med_id = self.medicament_by_name.get(medicament_nom.lower())
        if not med_id:
            return []
        mol_ids = self.med_mol_relations.get(med_id, [])
        return [self.molecule_by_id[mol_id] for mol_id in mol_ids if mol_id in self.molecule_by_id]

    def get_molecule_embedding(self, molecule_nom: str):
        return self.embedding_engine.encode(molecule_nom)

    def get_similar_molecules(self, text: str, threshold: float = 0.6):
        results = self.embedding_engine.find_similar(text, self.molecule_names, threshold=threshold)
        return [(nom, sim, self.molecule_by_name[nom.lower()]) for nom, sim in results]

    def get_similar_molecules_optimized(self, text: str, threshold: float = 0.6) -> List[Tuple[str, float, int]]:
        return self.get_similar_molecules(text, threshold)

    def detect_interactions_optimized(self, medicament_ids: List[int]) -> List[Tuple]:
        all_molecules = []
        for med_id in medicament_ids:
            all_molecules.extend(self.med_mol_relations.get(med_id, []))
        all_molecules = list(set(all_molecules))

        detected = []
        for i, mol1 in enumerate(all_molecules):
            for mol2 in all_molecules[i + 1:]:
                for mol2_interact, niveau, desc, reco in self.interactions_by_molecule.get(mol1, []):
                    if mol2_interact == mol2:
                        detected.append((mol1, mol2, niveau, desc, reco))
        return detected

    def detect_interactions(self, medicament_ids: List[int]):
        return self.detect_interactions_optimized(medicament_ids)

    def get_patient_allergies(self, patient_id: int):
        allergies = self.allergies_by_patient.get(patient_id, [])
        result = []
        for mol_id, type_alle, gravite in allergies:
            molecule = self.molecule_by_id.get(mol_id, {})
            if molecule:
                result.append((mol_id, molecule.get('nom'), type_alle, gravite))
        return result

    def check_allergies(self, patient_id: int, medicament_ids: List[int]):
        patient_allergies = self.allergies_by_patient.get(patient_id, [])
        patient_mol_ids = [a[0] for a in patient_allergies]
        med_molecules = []
        for med_id in medicament_ids:
            med_molecules.extend(self.med_mol_relations.get(med_id, []))
        med_molecules = list(set(med_molecules))

        detected = []
        for mol_id in med_molecules:
            if mol_id in patient_mol_ids:
                for allergie in patient_allergies:
                    if allergie[0] == mol_id:
                        molecule_name = self.molecule_by_id.get(mol_id, {}).get('nom', str(mol_id))
                        detected.append((mol_id, molecule_name, allergie[1], allergie[2]))
                        break
        return detected

    def get_alternatives(self, medicament_id: int, threshold: float = 0.5) -> List[Tuple[str, float]]:
        return self.get_alternatives_optimized(medicament_id, threshold)

    def get_alternatives_optimized(self, medicament_id: int, threshold: float = 0.5) -> List[Tuple[str, float]]:
        med_info = self.medicament_by_id.get(medicament_id)
        if not med_info:
            return []

        mols = self.med_mol_relations.get(medicament_id, [])
        mol_names = [self.molecule_by_id[mol_id]['nom'] for mol_id in mols if mol_id in self.molecule_by_id]
        search_texts = [med_info['nom']] + mol_names if med_info['nom'] else mol_names

        alternatives = {}
        for text in search_texts:
            results = self.embedding_engine.find_similar(text, self.medicament_names, threshold=threshold)
            for nom, sim in results:
                if nom.lower() != med_info['nom'].lower():
                    alternatives[nom] = max(alternatives.get(nom, 0.0), sim)

        return sorted(alternatives.items(), key=lambda item: item[1], reverse=True)[:10]

    def get_molecule_id_by_name(self, name: str):
        return self.molecule_by_name.get(name.lower())

    def get_patient_by_id(self, patient_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT idPatient, nom, prenom, dateNaissance, sexe, telephone FROM Patient WHERE idPatient = ?", (patient_id,))
        patient = cursor.fetchone()
        conn.close()
        return patient

    def get_cache_stats(self) -> Dict[str, Any]:
        return self.embedding_engine.get_cache_stats()
