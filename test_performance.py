import time
from src.nlp.optimized_semantic_engine import OptimizedSemanticEngine


def test_performance():
    print('📊 TEST DE PERFORMANCE\n' + '=' * 60)

    start = time.time()
    engine = OptimizedSemanticEngine()
    load_time = time.time() - start
    print(f'⏱️ Chargement du moteur : {load_time:.2f}s')

    start = time.time()
    for _ in range(10):
        engine.get_molecule_embedding('Aspirine')
    embed_time = time.time() - start
    print(f'⏱️ 10 embeddings (avec cache) : {embed_time:.3f}s')

    start = time.time()
    results = engine.get_similar_molecules('aspirine', threshold=0.5)
    search_time = time.time() - start
    print(f'⏱️ Recherche sémantique : {search_time:.3f}s')
    print(f'   Résultats trouvés : {len(results)}')

    start = time.time()
    interactions = engine.detect_interactions([1, 3])
    inter_time = time.time() - start
    print(f'⏱️ Détection d\'interactions : {inter_time:.3f}s')

    print('\n' + '=' * 60)
    print('📋 RÉSULTATS :')
    print(f"   Chargement : {load_time:.2f}s")
    print(f"   Embeddings : {embed_time:.3f}s")
    print(f"   Recherche  : {search_time:.3f}s")
    print(f"   Interactions: {inter_time:.3f}s")


if __name__ == '__main__':
    test_performance()
