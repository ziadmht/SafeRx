import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'safeRx.db'


def cleanup_statuses():
    conn = sqlite3.connect(DB_PATH)
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
        print(f"{sql}: {cur.rowcount}")

    conn.commit()
    conn.close()
    print('Cleanup status ok')


if __name__ == '__main__':
    cleanup_statuses()
