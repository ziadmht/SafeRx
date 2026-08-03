# src/api/api_server.py - Version finale avec toutes les corrections
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import List, Optional
import sqlite3
import uvicorn

from src.core.interaction_detector import InteractionDetector
from src.core.history_manager import HistoryManager
from src.core.patient_manager import PatientManager
from src.core.facture_manager import FactureManager
from src.database.db_manager import DatabaseManager
from src.nlp.optimized_semantic_engine import OptimizedSemanticEngine
from src.core.facture_generator import envoyer_a_paiement

# ============================================================
# INSTANCES GLOBALES
# ============================================================
_engine_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[SafeRx API] Démarrage de l'API SafeRx...")
    _engine_state["detector"] = InteractionDetector(engine_class=OptimizedSemanticEngine)
    _engine_state["history"] = HistoryManager()
    _engine_state["db"] = DatabaseManager()
    _engine_state["patient_manager"] = PatientManager()
    _engine_state["facture_manager"] = FactureManager()
    print("[SafeRx API] API prête")
    yield
    _engine_state.clear()

app = FastAPI(
    title="SafeRx API",
    description="API de réception d'ordonnances scannées",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================
# MODÈLES
# ============================================================
class PatientData(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    dateNaissance: Optional[str] = None
    sexe: Optional[str] = "M"
    telephone: Optional[str] = None

class OrdonnanceRequest(BaseModel):
    nss: str
    medicaments: List[str]
    patient: Optional[PatientData] = None

class ValidationRequest(BaseModel):
    analyse_id: int
    action: str  # "valider" ou "annuler"

# ============================================================
# ENDPOINTS
# ============================================================
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SafeRx API", "version": "1.0.0"}

@app.post("/analyse")
async def analyser_ordonnance(request: OrdonnanceRequest):
    """Reçoit une ordonnance scannée - PAS de facture ici."""
    detector = _engine_state["detector"]
    history = _engine_state["history"]
    db = _engine_state["db"]
    patient_manager = _engine_state["patient_manager"]

    patient_dict = request.patient.model_dump() if request.patient else None
    try:
        patient = patient_manager.get_or_create_by_nss(request.nss, patient_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur patient : {e}")

    med_ids = []
    introuvables = []
    for nom in request.medicaments:
        nom_norm = nom.strip()
        result = db.execute_query(
            "SELECT idMedicament FROM Medicament WHERE LOWER(nom) = LOWER(?)",
            (nom_norm,)
        )
        if result:
            med_ids.append(result[0][0])
        else:
            introuvables.append(nom)

    if introuvables:
        raise HTTPException(
            status_code=404,
            detail=f"Médicament(s) non trouvé(s) : {', '.join(introuvables)}"
        )

    resultat = detector.analyser_ordonnance(patient['id'], med_ids)
    analyse_id = history.enregistrer_analyse(patient['id'], med_ids, resultat)

    return {
        "analyse_id": analyse_id,
        "statut": "securisee" if resultat.est_securise else "alerte",
        "statut_validation": "EN_ATTENTE",
        "patient": patient,
        "medicaments": resultat.medicaments,
        "nb_alertes": len(resultat.alertes),
        "alertes": [
            {
                "type": a.type_alerte,
                "niveau": a.niveau,
                "message": a.message,
                "description": a.description,
                "recommandation": a.recommandation,
                "medicaments": a.medicaments_concernee
            } for a in resultat.alertes
        ]
    }

@app.post("/valider")
async def valider_ordonnance(request: ValidationRequest):
    """
    Valide une ordonnance et génère la facture.
    ✅ Transition atomique (AND statut_validation = 'En attente')
    ✅ Une seule facture par analyse (UNIQUE(idAnalyse))
    """
    db = _engine_state["db"]
    facture_manager = _engine_state["facture_manager"]
    history = _engine_state["history"]
    
    # ✅ Transition atomique : seul le premier gagnant continue
    rows_updated = db.execute_write_rowcount(
        "UPDATE Analyse SET statut_validation = 'VALIDEE' WHERE idAnalyse = ? AND statut_validation = 'EN_ATTENTE'",
        (request.analyse_id,)
    )
    
    if rows_updated == 0:
        raise HTTPException(
            status_code=409,
            detail="Analyse déjà traitée (conflit de concurrence)."
        )
    
    if request.action == "annuler":
        # Mise à jour pour annulation
        db.execute_write("""
            UPDATE Analyse 
            SET statut_validation = 'ANNULEE', 
                date_validation = CURRENT_TIMESTAMP
            WHERE idAnalyse = ?
        """, (request.analyse_id,))
        return {"status": "success", "action": "annulée"}
    
    # ✅ Action : valider
    # Récupérer les détails
    details = history.get_analyse_details(request.analyse_id)
    patient_id = details.get('patient_id') or db.execute_query(
        "SELECT idPatient FROM Analyse WHERE idAnalyse = ?", (request.analyse_id,)
    )[0][0]
    medicaments = details.get('medicaments', [])
    
    # Générer la facture
    ok, msg, facture = facture_manager.generer_facture(
        request.analyse_id,
        patient_id,
        medicaments,
        db
    )
    
    if not ok:
        # Rollback : remettre en attente
        db.execute_write(
            "UPDATE Analyse SET statut_validation = 'EN_ATTENTE' WHERE idAnalyse = ?",
            (request.analyse_id,)
        )
        raise HTTPException(status_code=500, detail=f"Erreur facturation : {msg}")
    
    # Simuler le paiement externe
    paiement = envoyer_a_paiement(facture)
    facture_manager.payer(facture['id'], paiement['reference'])
    
    # Récupérer la facture complète
    facture_complete = facture_manager.get_by_id(facture['id'])
    
    return {
        "status": "success",
        "action": "validée",
        "facture": facture_complete,
        "paiement": paiement
    }

@app.get("/factures")
async def get_factures(patient_id: Optional[int] = None):
    """Récupère les factures (optionnellement par patient)."""
    facture_manager = _engine_state["facture_manager"]
    db = _engine_state["db"]
    
    if patient_id:
        return facture_manager.get_by_patient(patient_id)
    else:
        rows = db.execute_query("""
            SELECT f.idFacture, f.numero, f.date_emission, f.montant_total, f.statut,
                   p.nom, p.prenom
            FROM Facture f
            JOIN Patient p ON f.idPatient = p.idPatient
            ORDER BY f.date_emission DESC
        """)
        
        return [
            {
                'id': r[0],
                'numero': r[1],
                'date_emission': r[2],
                'montant_total': r[3],
                'statut': r[4],
                'patient': f"{r[5]} {r[6]}"
            }
            for r in rows
        ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)