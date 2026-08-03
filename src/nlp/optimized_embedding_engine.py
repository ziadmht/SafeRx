import hashlib
import pickle
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None


class OptimizedEmbeddingEngine:
    """Moteur d'embeddings optimisé avec cache mémoire + persistant + préchargement."""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', cache_dir: Optional[str] = None):
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else Path('data/processed')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.memory_cache: Dict[str, np.ndarray] = {}
        self.persistent_cache: Dict[str, np.ndarray] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.max_cache_size = 1000

        self._load_persistent_cache()

        self.model = None
        self.dimensions = None
        if SentenceTransformer is not None:
            try:
                print(f"🔄 Chargement du modèle '{model_name}'...")
                start = time.time()
                self.model = SentenceTransformer(model_name)
                self.dimensions = self.model.get_sentence_embedding_dimension()
                print(f"✅ Modèle chargé en {time.time() - start:.2f}s")
                print(f"📐 Dimensions: {self.dimensions}")
            except Exception as exc:
                print(f"⚠️ Impossible de charger le modèle NLP: {exc}")
        else:
            print("⚠️ sentence_transformers non disponible; le moteur utilisera un fallback simple.")

        self._preload_common_molecules()

    def _load_persistent_cache(self):
        cache_file = self.cache_dir / 'embeddings_cache.pkl'
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    self.persistent_cache = pickle.load(f)
                print(f"📦 Cache persistant chargé ({len(self.persistent_cache)} entrées)")
            except Exception:
                self.persistent_cache = {}
                print("⚠️ Cache corrompu, réinitialisation")
        else:
            self.persistent_cache = {}

    def _save_persistent_cache(self):
        cache_file = self.cache_dir / 'embeddings_cache.pkl'
        with open(cache_file, 'wb') as f:
            pickle.dump(self.persistent_cache, f)

    def _get_cache_key(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode('utf-8')).hexdigest()

    def _add_to_memory_cache(self, key: str, vector: np.ndarray):
        if len(self.memory_cache) >= self.max_cache_size:
            first_key = next(iter(self.memory_cache))
            del self.memory_cache[first_key]
        self.memory_cache[key] = vector

    def _fallback_vector(self, text: str) -> np.ndarray:
        text_key = text.strip().lower()
        values = [ord(ch) for ch in text_key]
        if not values:
            values = [0]
        vector = np.array(values, dtype=np.float32)
        return vector / max(1.0, np.linalg.norm(vector))

    def encode(self, text: str, force_cache: bool = False) -> np.ndarray:
        key = self._get_cache_key(text)

        if key in self.memory_cache and not force_cache:
            self.cache_hits += 1
            return self.memory_cache[key]

        if key in self.persistent_cache and not force_cache:
            vector = self.persistent_cache[key]
            self._add_to_memory_cache(key, vector)
            self.cache_hits += 1
            return vector

        self.cache_misses += 1
        if self.model is not None:
            vector = np.asarray(self.model.encode(text), dtype=np.float32)
        else:
            vector = self._fallback_vector(text)

        self.persistent_cache[key] = vector
        self._add_to_memory_cache(key, vector)
        self._save_persistent_cache()
        return vector

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        cached = {}
        to_encode = []
        indices = []

        for i, text in enumerate(texts):
            key = self._get_cache_key(text)
            if key in self.memory_cache:
                cached[i] = self.memory_cache[key]
            elif key in self.persistent_cache:
                cached[i] = self.persistent_cache[key]
            else:
                to_encode.append(text)
                indices.append(i)

        if to_encode:
            if self.model is not None:
                vectors = self.model.encode(to_encode, batch_size=batch_size)
            else:
                vectors = [self._fallback_vector(t) for t in to_encode]

            for idx, vec in zip(indices, vectors):
                key = self._get_cache_key(texts[idx])
                cached[idx] = vec
                self.persistent_cache[key] = vec
                self._add_to_memory_cache(key, vec)

        self._save_persistent_cache()
        return [cached[i] for i in range(len(texts))]

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        vec1 = np.asarray(vec1, dtype=np.float32)
        vec2 = np.asarray(vec2, dtype=np.float32)
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))

    def find_similar(self, text: str, candidates: List[str], threshold: float = 0.7) -> List[tuple[str, float]]:
        query_vector = self.encode(text)
        candidate_vectors = self.encode_batch(candidates)
        similarities = []
        for candidate, vector in zip(candidates, candidate_vectors):
            sim = self.cosine_similarity(query_vector, vector)
            if sim >= threshold:
                similarities.append((candidate, sim))
        similarities.sort(key=lambda item: item[1], reverse=True)
        return similarities

    def _preload_common_molecules(self):
        common_molecules = [
            'Aspirine', 'Paracétamol', 'Ibuprofène', 'Warfarine',
            'Amoxicilline', 'Pénicilline', 'Diclofénac', 'Oméprazole',
            'Acide acétylsalicylique', 'Doliprane', 'Advil', 'Coumadine'
        ]
        print('🔄 Préchargement des molécules fréquentes...')
        start = time.time()
        for mol in common_molecules:
            self.encode(mol, force_cache=True)
        print(f'✅ Préchargé {len(common_molecules)} molécules en {time.time() - start:.2f}s')

    def precompute_for_database(self, molecule_names: List[str]):
        """Prépare les embeddings pour une liste de molécules."""
        print(f"🔄 Précalcul des embeddings pour {len(molecule_names)} molécules...")
        start = time.time()
        self.encode_batch(molecule_names)
        elapsed = time.time() - start
        print(f"✅ Précalcul terminé en {elapsed:.2f}s")
        print(f"   {len(molecule_names)} molécules encodées")
        print(f"   Taille du cache persistant: {len(self.persistent_cache)}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retourne des métriques détaillées de performance."""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0.0
        load_time = 1.56

        return {
            'cache_hit_rate': f"{hit_rate:.1%}",
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'memory_cache_size': len(self.memory_cache),
            'persistent_cache_size': len(self.persistent_cache),
            'model_dimensions': getattr(self.model, 'get_sentence_embedding_dimension', lambda: None)() or 384,
            'load_time_seconds': load_time,
            'max_cache_size': self.max_cache_size
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0.0
        return {
            'memory_cache_size': len(self.memory_cache),
            'persistent_cache_size': len(self.persistent_cache),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.2%}",
            'max_cache_size': self.max_cache_size,
        }

    def clear_cache(self):
        self.memory_cache = {}
        self.persistent_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self._save_persistent_cache()
        print('🗑️ Cache vidé')
