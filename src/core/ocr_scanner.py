# src/core/ocr_scanner.py
import re
import os
import sqlite3
import unicodedata
import difflib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("pytesseract non installe. pip install pytesseract pillow")

try:
    import pdf2image
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("pdf2image non installe. pip install pdf2image")


def normaliser(texte: str) -> str:
    """Minuscule + suppression des accents, pour comparaison robuste."""
    texte = texte.lower().strip()
    texte = unicodedata.normalize('NFKD', texte)
    texte = ''.join(c for c in texte if not unicodedata.combining(c))
    return texte


class OCRScanner:
    """
    Scanner d'ordonnances : extrait le texte, puis matche contre la liste
    RÉELLE des médicaments en base (whitelist), avec tolérance aux erreurs OCR.
    """

    def __init__(self, db_path=None):
        if not TESSERACT_AVAILABLE:
            raise ValueError("pytesseract non installe. pip install pytesseract pillow")

        # Configurer le chemin Tesseract (Windows)
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "safeRx.db"

        # medicaments_ref : { "nom_normalise": "Nom original tel qu'en base" }
        self.medicaments_ref = {}
        try:
            conn = sqlite3.connect(db_path)
            for (nom,) in conn.execute("SELECT nom FROM Medicament"):
                self.medicaments_ref[normaliser(nom)] = nom
            conn.close()
        except Exception as e:
            print(f"Impossible de charger les medicaments depuis la base : {e}")

        print(f"📷 Tesseract OCR pret ({len(self.medicaments_ref)} medicaments references)")

    def scanner_image(self, image_file) -> Dict:
        """Extrait les informations d'une ordonnance depuis une image."""
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image, lang='fra+eng')
        # ✅ Remettre le curseur à 0 pour permettre une réutilisation du fichier (ex: affichage)
        image_file.seek(0)
        return self._parser_texte(text)

    def scanner_pdf(self, pdf_file) -> Dict:
        """Extrait les informations d'une ordonnance depuis un PDF."""
        if not PDF_AVAILABLE:
            raise ValueError("pdf2image non installe. pip install pdf2image")
        images = pdf2image.convert_from_bytes(pdf_file.read())
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img, lang='fra+eng') + "\n"
        pdf_file.seek(0)
        return self._parser_texte(text)

    def _extraire_nss(self, text: str) -> Optional[str]:
        """Extrait le NSS (15 chiffres) du texte."""
        match = re.search(r'\b(\d{15})\b', text)
        return match.group(1) if match else None

    def _trouver_medicaments(self, text: str) -> List[str]:
        """Recherche toute correspondance (exacte ou approchante) avec la whitelist."""
        trouves = []
        noms_ref_norm = list(self.medicaments_ref.keys())

        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Génère des candidats : la ligne entière, et des fenêtres de 1 à 3 mots
            mots = re.findall(r"[A-Za-zàâéèêëîïôöùûüç']+", line)
            candidats = set()
            candidats.add(line)
            for taille in (1, 2, 3):
                for i in range(len(mots) - taille + 1):
                    candidats.add(' '.join(mots[i:i + taille]))

            for candidat in candidats:
                cand_norm = normaliser(candidat)
                if len(cand_norm) < 4:
                    continue

                # 1. Correspondance exacte ou par inclusion
                for ref_norm, ref_original in self.medicaments_ref.items():
                    if ref_norm == cand_norm or ref_norm in cand_norm or cand_norm in ref_norm:
                        if ref_original not in trouves:
                            trouves.append(ref_original)

                # 2. Correspondance approchante (tolère les erreurs OCR)
                proches = difflib.get_close_matches(cand_norm, noms_ref_norm, n=1, cutoff=0.82)
                if proches:
                    ref_original = self.medicaments_ref[proches[0]]
                    if ref_original not in trouves:
                        trouves.append(ref_original)

        return trouves

    def _parser_texte(self, text: str) -> Dict:
        """Parse le texte extrait pour retourner NSS et médicaments."""
        return {
            'nss': self._extraire_nss(text),
            'medicaments': self._trouver_medicaments(text),
            'patient': {}
        }

    def valider_donnees(self, data: Dict) -> Tuple[bool, str]:
        """Valide les données extraites."""
        if not data.get('nss'):
            return False, "NSS non trouve dans l'ordonnance."
        if not data.get('medicaments'):
            return False, "Aucun medicament identifie dans l'ordonnance."
        return True, "Donnees valides"