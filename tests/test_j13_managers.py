import pytest
import sqlite3
from src.core.medicament_manager import MedicamentManager
from src.core.molecule_manager import MoleculeManager

def test_molecule_manager_crud(test_db):
    mol_mgr = MoleculeManager(db_path=test_db)
    
    # Add molecule
    ok, msg = mol_mgr.add("MoleculeTest", "FamilleTest", "C10H15N")
    # ✅ CORRIGE : affiche le message d'erreur si échec
    assert ok is True, f"Échec MoleculeManager.add : {msg}"
    assert "ajoutée" in msg
    
    # Get by name
    mol = mol_mgr.get_by_name("MoleculeTest")
    assert mol is not None
    assert mol['famille'] == "FamilleTest"
    mol_id = mol['id']
    
    # Get by id
    mol_by_id = mol_mgr.get_by_id(mol_id)
    assert mol_by_id['nom'] == "MoleculeTest"
    
    # Update molecule
    ok, msg = mol_mgr.update(mol_id, "MoleculeTestUpdated", "FamilleUpdated", "C10H15N2")
    assert ok is True, f"Échec MoleculeManager.update : {msg}"
    
    # Statistics
    stats = mol_mgr.get_statistics()
    assert stats['total'] >= 1
    
    # Delete molecule (no dependencies)
    ok, msg = mol_mgr.delete(mol_id)
    assert ok is True, f"Échec MoleculeManager.delete : {msg}"

def test_medicament_manager_crud(test_db):
    med_mgr = MedicamentManager(db_path=test_db)
    mol_mgr = MoleculeManager(db_path=test_db)
    
    # Add medicament
    ok, msg = med_mgr.add("MedTest", "CIS999", "Gélule", "100mg", 25.5)
    # ✅ CORRIGE : affiche le message d'erreur si échec
    assert ok is True, f"Échec MedicamentManager.add : {msg}"
    
    med = med_mgr.get_by_name("MedTest")
    assert med is not None
    med_id = med['id']
    
    # Update
    ok, msg = med_mgr.update(med_id, "MedTestMod", "CIS999", "Gélule", "200mg", 30.0)
    assert ok is True, f"Échec MedicamentManager.update : {msg}"
    
    # Add molecule association
    ok, msg = mol_mgr.add("MolAssoc", "Fam", "H2O")
    assert ok is True, f"Échec MoleculeManager.add (MolAssoc) : {msg}"
    mol = mol_mgr.get_by_name("MolAssoc")
    
    ok, msg = med_mgr.add_molecule(med_id, mol['id'])
    assert ok is True, f"Échec MedicamentManager.add_molecule : {msg}"
    
    mols = med_mgr.get_molecules(med_id)
    assert len(mols) == 1
    assert mols[0]['nom'] == "MolAssoc"
    
    # Remove molecule association
    ok, msg = med_mgr.remove_molecule(med_id, mol['id'])
    assert ok is True, f"Échec MedicamentManager.remove_molecule : {msg}"
    assert len(med_mgr.get_molecules(med_id)) == 0
    
    # Delete
    ok, msg = med_mgr.delete(med_id)
    assert ok is True, f"Échec MedicamentManager.delete : {msg}"
    
    # Clean up test molecule
    ok, msg = mol_mgr.delete(mol['id'])
    assert ok is True, f"Échec MoleculeManager.delete (nettoyage) : {msg}"