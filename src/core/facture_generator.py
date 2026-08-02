# src/core/facture_generator.py
from datetime import datetime
import random
from typing import List, Dict

def generer_facture(patient: dict, medicaments: List[str], resultat, db) -> dict:
    """
    Génère une facture en récupérant les prix réels depuis la base.
    """
    total = 0.0
    details = []
    
    for nom in medicaments:
        rows = db.execute_query(
            "SELECT nom, prix FROM Medicament WHERE LOWER(nom) = LOWER(?)",
            (nom.strip(),)
        )
        prix = rows[0][1] if rows and rows[0][1] is not None else 0.0
        total += prix
        details.append({"medicament": nom, "prix": prix})

    return {
        'numero': f"FAC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        'patient_id': patient['id'],
        'patient_nom': f"{patient['nom']} {patient['prenom']}",
        'details': details,
        'montant_total': round(total, 2),
        'date': datetime.now().isoformat(),
        'statut': 'Bloquée' if not resultat.est_securise else 'Validée',
        'nb_alertes': len(resultat.alertes),
        'est_securise': resultat.est_securise
    }


def envoyer_a_paiement(facture: dict) -> dict:
    """Simule l'envoi au système de paiement externe."""
    return {
        'status': 'success',
        'reference': facture['numero'],
        'message': 'Facture transmise au système de paiement (simulation)'
    }
