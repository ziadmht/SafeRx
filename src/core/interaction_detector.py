import streamlit as st
from dataclasses import dataclass
from typing import List, Tuple

from src.nlp.semantic_engine import SemanticEngine
from src.core.constants import Niveau


@dataclass
class Alert:
    """Structure pour une alerte"""

    niveau: str  # Niveau.ELEVE, Niveau.MOYEN, Niveau.FAIBLE
    type_alerte: str  # 'interaction', 'allergie', 'information'
    message: str
    description: str
    recommandation: str
    medicaments_concernee: List[str]
    color: str = None

    def __post_init__(self):
        """Détermine la couleur en fonction du niveau"""
        # ✅ CORRIGE : Utilise Niveau.ELEVE au lieu de 'Élevé'
        if self.niveau == Niveau.ELEVE:
            self.color = "🔴"
        elif self.niveau == Niveau.MOYEN:
            self.color = "🟠"
        else:
            self.color = "🟡"


@dataclass
class AnalyseResult:
    """Résultat d'une analyse d'ordonnance"""

    patient_id: int
    patient_nom: str
    medicaments: List[str]
    alertes: List[Alert]
    est_securise: bool
    resume: str


class InteractionDetector:
    """
    Détecteur d'interactions médicamenteuses et d'allergies.
    """

    def __init__(self, engine_class=None):
        self.engine = engine_class() if engine_class else SemanticEngine()
        print("[InteractionDetector] Détecteur d'interactions initialisé")

    def analyser_ordonnance(
        self,
        patient_id: int,
        medicament_ids: List[int]
    ) -> AnalyseResult:
        """
        Analyse complète d'une ordonnance.
        """

        alertes = []
        medicament_noms = []

        # Récupération des noms des médicaments
        for med_id in medicament_ids:
            for med in self.engine.medicaments:
                if med[0] == med_id:
                    medicament_noms.append(med[1])
                    break

        # =====================================================
        # 1. Détection des interactions
        # =====================================================

        interactions = self.engine.detect_interactions(medicament_ids)

        for mol1, mol2, niveau, desc, reco in interactions:

            nom1 = None
            nom2 = None

            for mol in self.engine.molecules:
                if mol[0] == mol1:
                    nom1 = mol[1]

                if mol[0] == mol2:
                    nom2 = mol[1]

            if nom1 and nom2:
                alertes.append(
                    Alert(
                        niveau=niveau,
                        type_alerte="interaction",
                        message=f"⚠️ Interaction entre {nom1} et {nom2}",
                        description=desc,
                        recommandation=reco,
                        medicaments_concernee=[nom1, nom2],
                    )
                )

        # =====================================================
        # 2. Vérification des allergies
        # =====================================================

        allergies = self.engine.check_allergies(
            patient_id,
            medicament_ids
        )

        for mol_id, nom, type_alle, gravite in allergies:

            med_concernes = []

            for med_id in medicament_ids:
                mols = self.engine.medicament_molecules.get(med_id, [])

                if mol_id in mols:
                    for med in self.engine.medicaments:
                        if med[0] == med_id:
                            med_concernes.append(med[1])
                            break

            if gravite == "Sévère":
                niveau = Niveau.ELEVE
            elif gravite == "Moyenne":
                niveau = Niveau.MOYEN
            else:
                niveau = Niveau.FAIBLE

            alertes.append(
                Alert(
                    niveau=niveau,
                    type_alerte="allergie",
                    message=f"⚠️ Allergie à {nom} détectée",
                    description=f"Le patient est allergique à {nom} ({type_alle}, {gravite})",
                    recommandation=f"Éviter tout médicament contenant {nom}",
                    medicaments_concernee=med_concernes,
                )
            )

        # =====================================================
        # Résumé
        # =====================================================

        # ✅ CORRIGE : Utilise Niveau.ELEVE au lieu de 'Élevé'
        alertes_critiques = [
            a for a in alertes
            if a.niveau == Niveau.ELEVE
        ]

        est_securise = len(alertes_critiques) == 0

        if est_securise:
            resume = (
                "✅ Ordonnance sécurisée : aucune interaction dangereuse détectée"
            )
        else:
            resume = (
                f"🔴 Attention : {len(alertes_critiques)} alerte(s) critique(s) détectée(s)"
            )

        alertes_non_critiques = [
            a for a in alertes
            if a.niveau != Niveau.ELEVE
        ]

        if alertes_non_critiques:
            resume += (
                f" | {len(alertes_non_critiques)} alerte(s) de prudence"
            )

        patient = self.engine.get_patient_by_id(patient_id)

        if patient:
            patient_nom = f"{patient[1]} {patient[2]}"
        else:
            patient_nom = "Inconnu"

        return AnalyseResult(
            patient_id=patient_id,
            patient_nom=patient_nom,
            medicaments=medicament_noms,
            alertes=alertes,
            est_securise=est_securise,
            resume=resume,
        )

    def afficher_alertes(self, resultat: AnalyseResult):
        """
        Affiche les alertes dans Streamlit.
        """

        if resultat.est_securise:
            st.success(resultat.resume)
        else:
            st.error(resultat.resume)

        st.write(f"**Patient :** {resultat.patient_nom}")
        st.write(f"**Médicaments :** {', '.join(resultat.medicaments)}")

        st.markdown("---")

        if not resultat.alertes:
            st.info("ℹ️ Aucune alerte à signaler")
            return

        st.subheader("📋 Alertes détectées")

        for alert in resultat.alertes:

            if alert.niveau == Niveau.ELEVE:
                bg_color = "#ffcccc"
                border_color = "#ff0000"

            elif alert.niveau == Niveau.MOYEN:
                bg_color = "#ffeedd"
                border_color = "#ff8800"

            else:
                bg_color = "#ffffcc"
                border_color = "#ffcc00"

            st.markdown(
                f"""
                <div style="
                    background-color:{bg_color};
                    padding:15px;
                    border-radius:10px;
                    border-left:5px solid {border_color};
                    margin:10px 0;
                ">
                    <h4>{alert.color} {alert.message}</h4>
                    <p><strong>Description :</strong> {alert.description}</p>
                    <p><strong>Recommandation :</strong> {alert.recommandation}</p>
                    <p><strong>Niveau :</strong> {alert.niveau}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if (
                alert.type_alerte == "interaction"
                and alert.medicaments_concernee
            ):
                with st.expander("💊 Voir les alternatives"):

                    for med_nom in alert.medicaments_concernee:

                        med_id = self.engine.medicament_by_name.get(
                            med_nom.lower()
                        )

                        if med_id:

                            alternatives = self.engine.get_alternatives(
                                med_id,
                                threshold=0.5,
                            )

                            st.write(f"**Alternatives à {med_nom} :**")

                            for alt_nom, sim in alternatives[:5]:
                                st.write(
                                    f"- {alt_nom} (similarité : {sim:.2%})"
                                )

    def get_alternatives_for_medicament(
        self,
        medicament_nom: str,
        threshold: float = 0.5,
    ) -> List[Tuple[str, float]]:
        """
        Retourne les alternatives d'un médicament.
        """

        med_id = self.engine.medicament_by_name.get(
            medicament_nom.lower()
        )

        if med_id:
            return self.engine.get_alternatives(
                med_id,
                threshold,
            )

        return []


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":

    print("🧪 TEST DU DÉTECTEUR D'INTERACTIONS")
    print("=" * 60)

    detector = InteractionDetector()

    print("\n📊 Test 1")

    resultat = detector.analyser_ordonnance(
        patient_id=1,
        medicament_ids=[1, 3],
    )

    print("Patient :", resultat.patient_nom)
    print("Médicaments :", ", ".join(resultat.medicaments))
    print("Résumé :", resultat.resume)

    for alert in resultat.alertes:
        print(f"{alert.niveau} - {alert.message}")

    print("\n📊 Test 2")

    resultat = detector.analyser_ordonnance(
        patient_id=1,
        medicament_ids=[5],
    )

    print("Patient :", resultat.patient_nom)
    print("Résumé :", resultat.resume)

    for alert in resultat.alertes:
        print(f"{alert.niveau} - {alert.message}")

    print("\n📊 Test 3")

    alternatives = detector.get_alternatives_for_medicament("Aspirine")

    for alt, sim in alternatives[:5]:
        print(f"{alt} ({sim:.2%})")

    print("\n✅ Tests terminés !")