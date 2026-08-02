import sqlite3
from pathlib import Path
from src.core.history_manager import HistoryManager
from src.core.report_generator import ReportGenerator
from src.core.interaction_detector import AnalyseResult, Alert

root = Path('c:/projet_stage')
db_path = root / 'data' / 'test_smoke.db'
if db_path.exists():
    db_path.unlink()

hm = HistoryManager(db_path=db_path)
resultat = AnalyseResult(
    patient_id=1,
    patient_nom='Test User',
    medicaments=['Aspirine', 'Coumadine'],
    alertes=[Alert(niveau='Élevé', type_alerte='interaction', message='Interaction détectée', description='Description', recommandation='Éviter', medicaments_concernee=['Aspirine', 'Coumadine'])],
    est_securise=False,
    resume='Alerte',
)
analyse_id = hm.enregistrer_analyse(1, [1, 3], resultat)
details = hm.get_analyse_details(analyse_id)
stats = hm.get_statistiques()
rapport = ReportGenerator().generer_rapport_analyse(details)
export_path = ReportGenerator().exporter_txt(rapport, 'smoke_test.txt')

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Analyse','Alerte_Historique','Analyse_Medicament')")
tables = cur.fetchall()
conn.close()

print('ANALYSE_ID', analyse_id)
print('HISTORIQUE_LEN', len(hm.get_historique(5)))
print('DETAILS_KEYS', sorted(details.keys()))
print('STATS_TOTAL', stats['total_analyses'])
print('RAPPORT_OK', rapport.startswith('='))
print('EXPORT_OK', export_path)
print('TABLES', tables)
