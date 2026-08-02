# src/core/scanner_simulator.py
import json
import re
from typing import Dict, List, Optional

# ✅ AJOUT DE L'IMPORT OCR
from .ocr_scanner import OCRScanner


class ScannerSimulator:
    """Simule un scanner d'ordonnances - NE MAINTIENT AUCUN ÉTAT."""
    
    PATIENTS_CONNUS = {
        "123456789012345": {"nom": "Benjelloun", "prenom": "Karim", "dateNaissance": "1982-03-15", "sexe": "M", "telephone": "0612345678"},
        "234567890123456": {"nom": "El Amrani", "prenom": "Fatima", "dateNaissance": "1990-07-22", "sexe": "F", "telephone": "0623456789"},
        "345678901234567": {"nom": "Alaoui", "prenom": "Mohammed", "dateNaissance": "1975-11-10", "sexe": "M", "telephone": "0634567890"},
        "456789012345678": {"nom": "Tazi", "prenom": "Sofia", "dateNaissance": "2000-05-05", "sexe": "F", "telephone": "0645678901"},
        "567890123456789": {"nom": "Bennis", "prenom": "Omar", "dateNaissance": "1952-09-30", "sexe": "M", "telephone": "0656789012"},
    }

    MEDICAMENTS_CONNUS = [
        "Aspirine", "Coumadine", "Doliprane", "Advil",
        "Amoxicilline Sandoz", "Voltarène", "Pénicilline G", "Mopral"
    ]

    def __init__(self):
        """Initialise le scanner avec l'OCR."""
        try:
            from pathlib import Path
            db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"
            self.ocr = OCRScanner(db_path=db_path)
            self._ocr_disponible = True
        except Exception as e:
            print(f"⚠️ OCR non disponible : {e}")
            self.ocr = None
            self._ocr_disponible = False

    def get_patients(self) -> Dict:
        return self.PATIENTS_CONNUS

    def get_medicaments(self) -> List[str]:
        return self.MEDICAMENTS_CONNUS

    def lire_fichier(self, fichier) -> dict:
        """Lit et valide un fichier JSON d'ordonnance scannée."""
        data = json.load(fichier)

        nss = (data.get("nss") or "").strip()
        medicaments = data.get("medicaments", [])
        patient_data = data.get("patient", {})

        if not nss:
            raise ValueError("Le fichier ne contient pas de NSS ('nss').")
        if not medicaments:
            raise ValueError("Le fichier ne contient aucun médicament ('medicaments').")

        if not patient_data and nss in self.PATIENTS_CONNUS:
            patient_data = self.PATIENTS_CONNUS[nss]

        return {"nss": nss, "medicaments": medicaments, "patient": patient_data}

    def scanner_image(self, fichier, nom_original: str = None) -> dict:
        """
        Scanne une ordonnance depuis une image ou un PDF.
        
        Args:
            fichier: objet fichier (UploadedFile ou BytesIO)
            nom_original: nom de fichier explicite (nécessaire si `fichier` est un
                          BytesIO sans attribut .name, ex. après une manipulation
                          des bytes pour préserver la position du curseur)
        
        Formats supportés : JPG, JPEG, PNG, BMP, TIFF, WEBP, PDF
        """
        if not self._ocr_disponible:
            raise ValueError("OCR non disponible. Vérifiez l'installation de Tesseract.")
        
        # ✅ Utiliser le nom explicite ou l'attribut .name
        filename = nom_original or getattr(fichier, 'name', '')
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        # ✅ Déterminer le type de fichier
        if extension == 'pdf':
            data = self.ocr.scanner_pdf(fichier)
        elif extension in ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']:
            data = self.ocr.scanner_image(fichier)
        else:
            # ✅ Si l'extension n'est pas reconnue, lever une erreur claire
            raise ValueError(f"Extension de fichier non reconnue : '{extension}'. Formats supportés : PDF, JPG, JPEG, PNG, BMP, TIFF, WEBP")
        
        # Nettoyer les médicaments avant retour (retrait des dosages et doublons)
        if data.get('medicaments'):
            medicaments_nettoies = []
            for med in data['medicaments']:
                med_clean = re.sub(r'\s*\d+\s*(mg|mcg|g|ml|ui|iu)', '', med, flags=re.IGNORECASE).strip()
                if med_clean and len(med_clean) > 2:
                    if med_clean.lower() not in [m.lower() for m in medicaments_nettoies]:
                        medicaments_nettoies.append(med_clean)
            data['medicaments'] = medicaments_nettoies

        # Valider les données extraites
        is_valid, msg = self.ocr.valider_donnees(data)
        if not is_valid:
            raise ValueError(msg)
        
        # Enrichir avec les données patient si disponibles
        if data['nss'] in self.PATIENTS_CONNUS:
            data['patient'] = self.PATIENTS_CONNUS[data['nss']]
        
        return data