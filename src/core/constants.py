# src/core/constants.py
"""Constantes centralisées pour SafeRx - Évite les bugs d'encodage Unicode."""

class Statut:
    """Statuts d'une analyse - Codes ASCII stables."""
    SECURISEE = "SECURISEE"
    ALERTE = "ALERTE"
    ANNULEE = "ANNULEE"
    EN_ATTENTE = "EN_ATTENTE"
    VALIDEE = "VALIDEE"

    LABELS = {
        SECURISEE: "Sécurisée",
        ALERTE: "Alerte",
        ANNULEE: "Annulée",
        EN_ATTENTE: "En attente",
        VALIDEE: "Validée",
    }

    COULEURS = {
        SECURISEE: "#22c55e",
        ALERTE: "#f59e0b",
        ANNULEE: "#94a3b8",
        EN_ATTENTE: "#f59e0b",
        VALIDEE: "#22c55e",
    }

    @classmethod
    def label(cls, code: str) -> str:
        """Retourne le libellé affichable pour un code."""
        return cls.LABELS.get(code, code)

    @classmethod
    def couleur(cls, code: str) -> str:
        """Retourne la couleur pour un code."""
        return cls.COULEURS.get(code, "#94a3b8")


class Niveau:
    """Niveaux d'alerte - Codes ASCII stables."""
    ELEVE = "ELEVE"
    MOYEN = "MOYEN"
    FAIBLE = "FAIBLE"

    LABELS = {
        ELEVE: "Élevé",
        MOYEN: "Moyen",
        FAIBLE: "Faible",
    }

    COULEURS = {
        ELEVE: "#dc2626",
        MOYEN: "#f59e0b",
        FAIBLE: "#3b82f6",
    }

    @classmethod
    def label(cls, code: str) -> str:
        """Retourne le libellé affichable pour un code."""
        return cls.LABELS.get(code, code)

    @classmethod
    def couleur(cls, code: str) -> str:
        """Retourne la couleur pour un code."""
        return cls.COULEURS.get(code, "#94a3b8")