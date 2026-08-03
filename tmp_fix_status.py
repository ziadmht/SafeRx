import sqlite3
from pathlib import Path

TARGET_STRINGS = [
    'En attente',
    'Validée',
    'Annulée',
    'Élevé',
    'Sécurisée',
    'EN_ATTENTE',
    'VALIDEE',
    'ANNULEE',
]

print('=== Audit Python ===')
found = 0
for path in sorted(Path('.').rglob('*.py')):
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    hits = [s for s in TARGET_STRINGS if s in text]
    if hits:
        found += 1
        print(f'{path}: {hits[:10]}')
print(f'Fichiers avec correspondances: {found}')

print('\n=== Nettoyage base ===')
db = Path('data/safeRx.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
updates = [
    "UPDATE Analyse SET statut_validation = 'EN_ATTENTE' WHERE statut_validation = 'En attente'",
    "UPDATE Analyse SET statut_validation = 'VALIDEE' WHERE statut_validation = 'Validée'",
    "UPDATE Analyse SET statut_validation = 'ANNULEE' WHERE statut_validation = 'Annulée'",
    "UPDATE Analyse SET statut = 'SECURISEE' WHERE statut = 'Sécurisée'",
    "UPDATE Analyse SET statut = 'ALERTE' WHERE statut = 'Alerte'",
    "UPDATE Analyse SET statut = 'ANNULEE' WHERE statut = 'Annulée'",
    "UPDATE Facture SET statut = 'EN_ATTENTE' WHERE statut = 'En attente'",
    "UPDATE Facture SET statut = 'PAYEE' WHERE statut = 'Payée'",
    "UPDATE Facture SET statut = 'ANNULEE' WHERE statut = 'Annulée'",
]
for sql in updates:
    cur.execute(sql)
    print(f'{sql}: {cur.rowcount}')
conn.commit()
print('Analyse recente:')
for row in cur.execute("SELECT idAnalyse, statut, statut_validation, dateAnalyse FROM Analyse ORDER BY idAnalyse DESC LIMIT 10"):
    print(row)
print('Factures:')
for row in cur.execute("SELECT idFacture, statut FROM Facture ORDER BY idFacture DESC LIMIT 10"):
    print(row)
conn.close()
