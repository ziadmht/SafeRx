import sqlite3
import tempfile
from pathlib import Path

from src.core.history_manager import HistoryManager
from src.core.interaction_detector import AnalyseResult, Alert


def test_history_manager_persists_analysis_and_stats(tmp_path):
    db_path = tmp_path / "test_safeRx.db"
    manager = HistoryManager(db_path=db_path)

    resultat = AnalyseResult(
        patient_id=1,
        patient_nom="Test User",
        medicaments=["Aspirine", "Coumadine"],
        alertes=[
            Alert(
                niveau="Élevé",
                type_alerte="interaction",
                message="Interaction détectée",
                description="Description",
                recommandation="Éviter",
                medicaments_concernee=["Aspirine", "Coumadine"],
            )
        ],
        est_securise=False,
        resume="Alerte",
    )

    analyse_id = manager.enregistrer_analyse(1, [1, 3], resultat)

    assert analyse_id is not None
    historique = manager.get_historique(limit=5)
    assert len(historique) == 1
    assert historique[0]["statut"] == "Alerte"
    assert historique[0]["nb_alertes"] == 1

    details = manager.get_analyse_details(analyse_id)
    assert details["patient"] == "Benjelloun Karim"
    assert len(details["alertes"]) == 1


    stats = manager.get_statistiques()
    assert stats["total_analyses"] == 1
    assert stats["par_statut"]["Alerte"] == 1
