# test_embedding_engine.py
import unittest
import numpy as np
import shutil
from pathlib import Path
from src.nlp.embedding_engine import EmbeddingEngine

class TestEmbeddingEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Utiliser un dossier de cache temporaire pour les tests
        cls.test_cache_dir = Path("data/test_processed")
        cls.engine = EmbeddingEngine(cache_dir=cls.test_cache_dir)

    @classmethod
    def tearDownClass(cls):
        # Nettoyer le dossier de cache de test
        if cls.test_cache_dir.exists():
            shutil.rmtree(cls.test_cache_dir)

    def test_encode_returns_numpy_array(self):
        vector = self.engine.encode("test")
        self.assertIsInstance(vector, np.ndarray)
        self.assertEqual(vector.shape, (384,))

    def test_caching_mechanism(self):
        # Premier encodage (calculé)
        text = "aspirine"
        _ = self.engine.encode(text)
        self.assertIn(text, self.engine._cache)

        # Deuxième encodage (doit venir du cache)
        cache_file = self.test_cache_dir / 'embeddings_cache.pkl'
        self.assertTrue(cache_file.exists())

        # Recréer le moteur pour charger le cache depuis le disque
        new_engine = EmbeddingEngine(cache_dir=self.test_cache_dir)
        self.assertIn(text, new_engine._cache)

    def test_cosine_similarity(self):
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        # Même vecteur = similarité 1.0
        self.assertAlmostEqual(self.engine.cosine_similarity(vec1, vec2), 1.0)

        vec3 = np.array([0.0, 1.0, 0.0])
        # Vecteurs orthogonaux = similarité 0.0
        self.assertAlmostEqual(self.engine.cosine_similarity(vec1, vec3), 0.0)

    def test_find_similar(self):
        candidates = ["Paracétamol", "Ibuprofène", "Aspirine"]
        results = self.engine.find_similar("Doliprane", candidates, threshold=0.1)
        # Devrait retourner une liste de tuples (candidat, score) triée par score décroissant
        self.assertTrue(len(results) > 0)
        for cand, score in results:
            self.assertIn(cand, candidates)
            self.assertGreaterEqual(score, 0.1)
        
        # Vérifier le tri décroissant
        scores = [score for _, score in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_are_similar(self):
        # "Advil" et "Ibuprofène" devraient être similaires avec un seuil de 0.5
        self.assertTrue(self.engine.are_similar("Advil", "Ibuprofène", threshold=0.5))
        # "Aspirine" et "Paracétamol" ne devraient pas l'être
        self.assertFalse(self.engine.are_similar("Aspirine", "Paracétamol", threshold=0.7))

if __name__ == "__main__":
    unittest.main()
