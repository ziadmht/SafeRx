from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class ReportGenerator:
    """Générateur de rapports pour SafeRx."""

    def generer_rapport_analyse(self, analyse_details: Dict[str, Any]) -> str:
        rapport = []
        rapport.append("=" * 60)
        rapport.append("          SAFERX - RAPPORT D'ANALYSE")
        rapport.append("=" * 60)
        rapport.append("")
        rapport.append(f"📅 Date : {analyse_details['date']}")
        rapport.append(f"👤 Patient : {analyse_details['patient']}")
        rapport.append(f"📊 Statut : {analyse_details['statut']}")
        rapport.append(f"⚠️ Alertes : {analyse_details['nb_alertes']}")
        rapport.append("")
        rapport.append("💊 Médicaments analysés :")
        for med in analyse_details.get("medicaments", []):
            rapport.append(f"   - {med}")
        rapport.append("")

        if analyse_details.get("alertes"):
            rapport.append("📋 ALERTES DÉTECTÉES :")
            rapport.append("")
            for i, alerte in enumerate(analyse_details["alertes"], 1):
                rapport.append(f"--- Alerte {i} ---")
                rapport.append(f"   Type : {alerte['type']}")
                rapport.append(f"   Niveau : {alerte['niveau']}")
                rapport.append(f"   Message : {alerte['message']}")
                rapport.append(f"   Description : {alerte['description']}")
                rapport.append(f"   Recommandation : {alerte['recommandation']}")
                rapport.append(f"   Médicaments : {alerte['medicaments']}")
                rapport.append("")
        else:
            rapport.append("✅ Aucune alerte détectée - Ordonnance sécurisée")

        rapport.append("")
        rapport.append("=" * 60)
        rapport.append("Rapport généré le " + datetime.now().strftime("%d/%m/%Y à %H:%M"))
        rapport.append("SafeRx - Assistant Intelligent de Délivrance")
        rapport.append("=" * 60)

        return "\n".join(rapport)

    def generer_rapport_global(self, statistiques: Dict[str, Any]) -> str:
        rapport = []
        rapport.append("=" * 60)
        rapport.append("       SAFERX - RAPPORT GLOBAL D'ACTIVITÉ")
        rapport.append("=" * 60)
        rapport.append("")
        rapport.append(f"📊 Total d'analyses : {statistiques.get('total_analyses', 0)}")
        rapport.append("")
        rapport.append("📈 RÉPARTITION PAR STATUT :")
        for statut, count in statistiques.get("par_statut", {}).items():
            rapport.append(f"   - {statut} : {count}")
        rapport.append("")
        rapport.append("📈 RÉPARTITION PAR TYPE D'ALERTE :")
        for type_alerte, count in statistiques.get("par_type_alerte", {}).items():
            rapport.append(f"   - {type_alerte} : {count}")
        rapport.append("")
        rapport.append("📈 RÉPARTITION PAR NIVEAU D'ALERTE :")
        for niveau, count in statistiques.get("par_niveau_alerte", {}).items():
            rapport.append(f"   - {niveau} : {count}")
        rapport.append("")
        rapport.append("=" * 60)
        rapport.append("Rapport généré le " + datetime.now().strftime("%d/%m/%Y à %H:%M"))
        rapport.append("SafeRx - Assistant Intelligent de Délivrance")
        rapport.append("=" * 60)

        return "\n".join(rapport)

    def exporter_txt(self, contenu: str, nom_fichier: str = None) -> str:
        if nom_fichier is None:
            nom_fichier = f"rapport_saferx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        rapports_dir = Path(__file__).parent.parent.parent / "data" / "rapports"
        rapports_dir.mkdir(parents=True, exist_ok=True)

        chemin = rapports_dir / nom_fichier
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)

        return str(chemin)
