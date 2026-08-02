# src/nlp/embedding_engine.py
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import pickle
import time

class EmbeddingEngine:
    """
    Moteur d'embeddings pour SafeRx.
    Gère la transformation de texte en vecteurs et le calcul de similarité.
    """

    def __init__(self, model_name='all-MiniLM-L6-v2', cache_dir=None):
        """
        Initialise le moteur d'embeddings.

        Args:
            model_name: Nom du modèle Sentence Transformers
            cache_dir: Dossier pour mettre en cache les embeddings
        """
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else Path('data/processed')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        print(f"--- Chargement du modele '{model_name}'...")
        self.model = SentenceTransformer(model_name)
        print(f"[OK] Modele charge (dimensions: {self.model.get_sentence_embedding_dimension()})")

        # Cache pour éviter de recalculer les embeddings
        self._cache = {}
        self._load_cache()

    def _load_cache(self):
        """Charge le cache des embeddings depuis le disque"""
        cache_file = self.cache_dir / 'embeddings_cache.pkl'
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    self._cache = pickle.load(f)
                print(f"[OK] Cache charge ({len(self._cache)} entrees)")
            except:
                self._cache = {}
                print("[WARNING] Cache corrompu, reinitialisation")

    def _save_cache(self):
        """Sauvegarde le cache des embeddings sur le disque"""
        cache_file = self.cache_dir / 'embeddings_cache.pkl'
        with open(cache_file, 'wb') as f:
            pickle.dump(self._cache, f)

    def encode(self, text):
        """
        Transforme un texte en vecteur (embedding).
        Avec mise en cache pour les appels répétés.

        Args:
            text: Texte à encoder

        Returns:
            np.ndarray: Vecteur d'embedding
        """
        # Nettoyer le texte
        text = text.strip().lower()

        # Vérifier le cache
        if text in self._cache:
            return self._cache[text]

        # Calculer l'embedding
        vector = self.model.encode(text)

        # Mettre en cache
        self._cache[text] = vector
        self._save_cache()

        return vector

    def encode_batch(self, texts):
        """
        Transforme une liste de textes en vecteurs.

        Args:
            texts: Liste de textes

        Returns:
            list: Liste de vecteurs d'embedding
        """
        return [self.encode(t) for t in texts]

    def cosine_similarity(self, vec1, vec2):
        """
        Calcule la similarité cosinus entre deux vecteurs.

        Args:
            vec1: Premier vecteur
            vec2: Deuxième vecteur

        Returns:
            float: Similarité entre 0 et 1
        """
        # Convertir en numpy arrays si besoin
        if not isinstance(vec1, np.ndarray):
            vec1 = np.array(vec1)
        if not isinstance(vec2, np.ndarray):
            vec2 = np.array(vec2)

        # Calcul de la similarité cosinus
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # ✅ IMPORTANT : Convertir en float pour les tests
        return float(dot_product / (norm1 * norm2))

    def find_similar(self, text, candidates, threshold=0.7):
        """
        Trouve les textes similaires à un texte donné.

        Args:
            text: Texte de référence
            candidates: Liste des textes candidats
            threshold: Seuil de similarité (0-1)

        Returns:
            list: Liste des (candidat, similarité) triés par similarité
        """
        # Encoder le texte de référence
        query_vector = self.encode(text)

        # Encoder tous les candidats
        candidate_vectors = self.encode_batch(candidates)

        # Calculer les similarités
        similarities = []
        for i, candidate in enumerate(candidates):
            sim = self.cosine_similarity(query_vector, candidate_vectors[i])
            if sim >= threshold:
                similarities.append((candidate, sim))

        # Trier par similarité décroissante
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities

    def are_similar(self, text1, text2, threshold=0.75):
        """
        Vérifie si deux textes sont sémantiquement similaires

        Args:
            text1: Premier texte
            text2: Deuxième texte
            threshold: Seuil de l'indice de similarité

        Returns:
            bool: True si les textes sont similaires
        """
        vec1 = self.encode(text1)
        vec2 = self.encode(text2)
        sim = self.cosine_similarity(vec1, vec2)
        return sim >= threshold


# ===========================================================
# TEST RAPIDE
# ===========================================================
if __name__ == "__main__":
    print("[TEST] TEST DU MOTEUR D'EMBEDDINGS\n" + "="*50)

    # Créer le moteur
    engine = EmbeddingEngine()

    # Test 1 : Similarité de base
    print("\n[TEST] Test 1 : Similarité de base")
    test_pairs = [
        ("Aspirine", "Acide acétylsalicylique"),
        ("Doliprane", "Paracétamol"),
        ("Advil", "Ibuprofène"),
        ("Aspirine", "Paracétamol"),
        ("Warfarine", "Coumadine"),
    ]

    for t1, t2 in test_pairs:
        vec1 = engine.encode(t1)
        vec2 = engine.encode(t2)
        sim = engine.cosine_similarity(vec1, vec2)
        status = "[OK] SIMILAIRE" if sim > 0.7 else "[INFO] DIFFERENT"
        print(f"  {t1:20} vs {t2:20} : {sim:.4f}  {status}")

    # Test 2 : Recherche de similaires
    print("\n[TEST] Test 2 : Recherche de textes similaires")
    query = "Aspirine"
    candidates = ["Acide acétylsalicylique", "Paracétamol", "Doliprane", "Ibuprofène", "Warfarine"]

    results = engine.find_similar(query, candidates, threshold=0.5)
    print(f"  Textes similaires à '{query}' :")
    for text, sim in results:
        print(f"    - {text:20} : {sim:.4f}")

    print("\n[OK] Tests termines !")