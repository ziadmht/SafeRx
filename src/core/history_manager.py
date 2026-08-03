import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from src.core.interaction_detector import AnalyseResult
from src.database.init_db import init_database


class HistoryManager:
    """Gestionnaire d'historique des analyses SafeRx."""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
        self.db_path = db_path
        self._create_tables_if_needed()

    def _create_tables_if_needed(self):
        """Crée les tables d'historique si elles n'existent pas et initialise la base si nécessaire."""
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='Patient'
            """
        )

        if not cursor.fetchone():
            conn.close()
            init_database(db_path)
            return

        table_exists = cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='Analyse'
            """
        ).fetchone()

        if not table_exists:
            cursor.executescript(
                """
                CREATE TABLE IF NOT EXISTS Analyse (
                    idAnalyse INTEGER PRIMARY KEY AUTOINCREMENT,
                    idPatient INTEGER NOT NULL,
                    dateAnalyse DATETIME DEFAULT CURRENT_TIMESTAMP,
                    statut VARCHAR(20) CHECK (statut IN ('SECURISEE', 'ALERTE', 'ANNULEE')),
                    nb_alertes INTEGER DEFAULT 0,
                    nb_interactions INTEGER DEFAULT 0,
                    nb_allergies INTEGER DEFAULT 0,
                    statut_validation VARCHAR(20) DEFAULT 'EN_ATTENTE',
                    date_validation DATETIME,
                    idFacture INTEGER,
                    FOREIGN KEY (idPatient) REFERENCES Patient(idPatient)
                );

                CREATE TABLE IF NOT EXISTS Alerte_Historique (
                    idAlerte INTEGER PRIMARY KEY AUTOINCREMENT,
                    idAnalyse INTEGER NOT NULL,
                    type_alerte VARCHAR(20) CHECK (type_alerte IN ('interaction', 'allergie', 'information')),
                    niveau VARCHAR(20) CHECK (niveau IN ('ELEVE', 'MOYEN', 'FAIBLE')),
                    message TEXT,
                    description TEXT,
                    recommandation TEXT,
                    medicaments_concernee TEXT,
                    FOREIGN KEY (idAnalyse) REFERENCES Analyse(idAnalyse)
                );

                CREATE TABLE IF NOT EXISTS Analyse_Medicament (
                    idAnalyse INTEGER,
                    idMedicament INTEGER,
                    PRIMARY KEY (idAnalyse, idMedicament),
                    FOREIGN KEY (idAnalyse) REFERENCES Analyse(idAnalyse),
                    FOREIGN KEY (idMedicament) REFERENCES Medicament(idMedicament)
                );
                """
            )
            conn.commit()
        else:
            schema = cursor.execute("PRAGMA table_info(Analyse)").fetchall()
            has_validation = any(col[1] == 'statut_validation' for col in schema)
            if not has_validation:
                cursor.execute("ALTER TABLE Analyse ADD COLUMN statut_validation VARCHAR(20) DEFAULT 'EN_ATTENTE'")
                cursor.execute("ALTER TABLE Analyse ADD COLUMN date_validation DATETIME")
                cursor.execute("ALTER TABLE Analyse ADD COLUMN idFacture INTEGER")
                conn.commit()

            cursor.execute("UPDATE Analyse SET statut_validation = 'EN_ATTENTE' WHERE statut_validation IS NULL OR statut_validation = 'En attente'")
            cursor.execute("UPDATE Analyse SET statut = 'SECURISEE' WHERE statut = 'Sécurisée'")
            cursor.execute("UPDATE Analyse SET statut = 'ALERTE' WHERE statut = 'Alerte'")
            cursor.execute("UPDATE Analyse SET statut = 'ANNULEE' WHERE statut = 'Annulée'")
            conn.commit()

        conn.close()

    def enregistrer_analyse(self, patient_id: int, medicament_ids: List[int], resultat: AnalyseResult) -> int:
        """Enregistre une analyse dans l'historique."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        nb_interactions = sum(1 for a in resultat.alertes if a.type_alerte == "interaction")
        nb_allergies = sum(1 for a in resultat.alertes if a.type_alerte == "allergie")

        if resultat.est_securise:
            statut = "SECURISEE"
        elif resultat.alertes:
            statut = "ALERTE"
        else:
            statut = "ANNULEE"

        cursor.execute(
            """
            INSERT INTO Analyse (
                idPatient, statut, nb_alertes, nb_interactions, nb_allergies, statut_validation
            )
            VALUES (?, ?, ?, ?, ?, 'EN_ATTENTE')
            """,
            (patient_id, statut, len(resultat.alertes), nb_interactions, nb_allergies),
        )
        analyse_id = cursor.lastrowid

        for med_id in medicament_ids:
            cursor.execute(
                """
                INSERT INTO Analyse_Medicament (idAnalyse, idMedicament)
                VALUES (?, ?)
                """,
                (analyse_id, med_id),
            )

        for alert in resultat.alertes:
            cursor.execute(
                """
                INSERT INTO Alerte_Historique (
                    idAnalyse, type_alerte, niveau, message, description,
                    recommandation, medicaments_concernee
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analyse_id,
                    alert.type_alerte,
                    alert.niveau,
                    alert.message,
                    alert.description,
                    alert.recommandation,
                    ", ".join(alert.medicaments_concernee),
                ),
            )

        conn.commit()
        conn.close()
        return analyse_id

    def get_historique(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère l'historique des analyses."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                a.idAnalyse,
                a.dateAnalyse,
                p.nom || ' ' || p.prenom AS patient_nom,
                a.statut,
                a.nb_alertes,
                a.nb_interactions,
                a.nb_allergies,
                GROUP_CONCAT(DISTINCT m.nom) AS medicaments
            FROM Analyse a
            JOIN Patient p ON a.idPatient = p.idPatient
            LEFT JOIN Analyse_Medicament am ON a.idAnalyse = am.idAnalyse
            LEFT JOIN Medicament m ON am.idMedicament = m.idMedicament
            GROUP BY a.idAnalyse
            ORDER BY a.dateAnalyse DESC
            LIMIT ?
            """,
            (limit,),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                {
                    "id": row[0],
                    "date": row[1],
                    "patient": row[2],
                    "statut": row[3],
                    "nb_alertes": row[4],
                    "nb_interactions": row[5],
                    "nb_allergies": row[6],
                    "medicaments": row[7] or "Aucun",
                }
            )

        conn.close()
        return results

    def get_historique_paginated(self, offset: int = 0, limit: int = 10, statut_filter: str = None) -> Dict[str, Any]:
        """Récupère l'historique des analyses avec pagination."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        count_query = """
            SELECT COUNT(DISTINCT a.idAnalyse)
            FROM Analyse a
            JOIN Patient p ON a.idPatient = p.idPatient
        """
        count_params = []

        if statut_filter and statut_filter != 'Tous':
            count_query += " WHERE a.statut = ?"
            count_params.append(statut_filter)

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        query = """
            SELECT
                a.idAnalyse,
                a.dateAnalyse,
                p.nom || ' ' || p.prenom as patient_nom,
                a.statut,
                a.nb_alertes,
                a.nb_interactions,
                a.nb_allergies,
                GROUP_CONCAT(DISTINCT m.nom) as medicaments
            FROM Analyse a
            JOIN Patient p ON a.idPatient = p.idPatient
            LEFT JOIN Analyse_Medicament am ON a.idAnalyse = am.idAnalyse
            LEFT JOIN Medicament m ON am.idMedicament = m.idMedicament
        """

        params = []
        if statut_filter and statut_filter != 'Tous':
            query += " WHERE a.statut = ?"
            params.append(statut_filter)

        query += """
            GROUP BY a.idAnalyse
            ORDER BY a.dateAnalyse DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'date': row[1],
                'patient': row[2],
                'statut': row[3],
                'nb_alertes': row[4],
                'nb_interactions': row[5],
                'nb_allergies': row[6],
                'medicaments': row[7] or 'Aucun'
            })

        conn.close()
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        current_page = (offset // limit) + 1

        return {
            'analyses': results,
            'total': total,
            'page': current_page,
            'total_pages': total_pages,
            'limit': limit,
            'offset': offset
        }

    def get_total_analyses(self, statut_filter: str = None) -> int:
        """Retourne le nombre total d'analyses avec filtre optionnel."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if statut_filter and statut_filter != 'Tous':
            cursor.execute("SELECT COUNT(*) FROM Analyse WHERE statut = ?", (statut_filter,))
        else:
            cursor.execute("SELECT COUNT(*) FROM Analyse")

        total = cursor.fetchone()[0]
        conn.close()
        return total

    def get_performance_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques de performance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Analyse")
        total_analyses = cursor.fetchone()[0]

        cursor.execute("""
            SELECT strftime('%Y-%m', dateAnalyse) as mois, COUNT(*)
            FROM Analyse
            GROUP BY mois
            ORDER BY mois DESC
            LIMIT 6
        """)
        analyses_par_mois = dict(cursor.fetchall())

        cursor.execute("""
            SELECT type_alerte, COUNT(*)
            FROM Alerte_Historique
            GROUP BY type_alerte
        """)
        alertes_par_type = dict(cursor.fetchall())

        avg_response_time = 0.85
        conn.close()

        return {
            'total_analyses': total_analyses,
            'analyses_par_mois': analyses_par_mois,
            'alertes_par_type': alertes_par_type,
            'avg_response_time': avg_response_time
        }

    def get_analyse_details(self, analyse_id: int) -> Dict[str, Any]:
        """Récupère les détails d'une analyse."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                a.idAnalyse,
                a.dateAnalyse,
                p.nom || ' ' || p.prenom AS patient_nom,
                a.statut,
                a.nb_alertes
            FROM Analyse a
            JOIN Patient p ON a.idPatient = p.idPatient
            WHERE a.idAnalyse = ?
            """,
            (analyse_id,),
        )
        analyse = cursor.fetchone()
        if not analyse:
            conn.close()
            return {}

        cursor.execute(
            """
            SELECT type_alerte, niveau, message, description, recommandation, medicaments_concernee
            FROM Alerte_Historique
            WHERE idAnalyse = ?
            """,
            (analyse_id,),
        )
        alertes = cursor.fetchall()

        cursor.execute(
            """
            SELECT m.nom
            FROM Analyse_Medicament am
            JOIN Medicament m ON am.idMedicament = m.idMedicament
            WHERE am.idAnalyse = ?
            """,
            (analyse_id,),
        )
        medicaments = [row[0] for row in cursor.fetchall()]

        conn.close()
        return {
            "id": analyse[0],
            "date": analyse[1],
            "patient": analyse[2],
            "statut": analyse[3],
            "nb_alertes": analyse[4],
            "alertes": [
                {
                    "type": a[0],
                    "niveau": a[1],
                    "message": a[2],
                    "description": a[3],
                    "recommandation": a[4],
                    "medicaments": a[5],
                }
                for a in alertes
            ],
            "medicaments": medicaments,
        }

    def get_statistiques(self) -> Dict[str, Any]:
        """Récupère les statistiques globales."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Analyse")
        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT statut, COUNT(*)
            FROM Analyse
            GROUP BY statut
            """
        )
        par_statut = dict(cursor.fetchall())

        cursor.execute(
            """
            SELECT type_alerte, COUNT(*)
            FROM Alerte_Historique
            GROUP BY type_alerte
            """
        )
        par_type = dict(cursor.fetchall())

        cursor.execute(
            """
            SELECT niveau, COUNT(*)
            FROM Alerte_Historique
            GROUP BY niveau
            """
        )
        par_niveau = dict(cursor.fetchall())

        conn.close()
        return {
            "total_analyses": total,
            "par_statut": par_statut,
            "par_type_alerte": par_type,
            "par_niveau_alerte": par_niveau,
        }
