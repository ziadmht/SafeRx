# tests/test_j14_api.py
import pytest
import asyncio
from src.api.api_server import health_check, analyser_ordonnance, valider_ordonnance, OrdonnanceRequest, PatientData, ValidationRequest, lifespan, app

def test_api_health():
    res = asyncio.run(health_check())
    assert res["status"] == "healthy"
    assert res["service"] == "SafeRx API"

def test_api_analyse_ordonnance():
    async def run_test():
        async with lifespan(app):
            # 1. Analyse de l'ordonnance (Scan)
            req = OrdonnanceRequest(
                nss="123456789012345",
                medicaments=["Aspirine", "Coumadine"],
                patient=PatientData(nom="Benjelloun", prenom="Karim")
            )
            res = await analyser_ordonnance(req)
            assert res["statut"] in ["securisee", "alerte"]
            assert res["patient"]["nss"] == "123456789012345"
            assert res["statut_validation"] == "En attente"
            
            # 2. Validation et facturation
            val_req = ValidationRequest(
                analyse_id=res["analyse_id"],
                action="valider"
            )
            val_res = await valider_ordonnance(val_req)
            assert val_res["status"] == "success"
            assert val_res["action"] == "validée"
            assert "numero" in val_res["facture"]
            assert "reference" in val_res["paiement"]
    
    asyncio.run(run_test())
