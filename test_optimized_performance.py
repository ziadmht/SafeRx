import time
from src.nlp.optimized_semantic_engine import OptimizedSemanticEngine
from src.nlp.semantic_engine import SemanticEngine


def compare_performance():
    print('📊 COMPARAISON DES PERFORMANCES\n' + '=' * 60)

    print('\n🔴 MOTEUR ANCIEN (sans optimisation)')
    start = time.time()
    old_engine = SemanticEngine()
    old_load = time.time() - start

    start = time.time()
    old_engine.get_similar_molecules('aspirine', threshold=0.5)
    old_search = time.time() - start

    print('\n🟢 MOTEUR OPTIMISÉ (avec cache avancé)')
    start = time.time()
    new_engine = OptimizedSemanticEngine(precompute=True)
    new_load = time.time() - start

    start = time.time()
    new_engine.get_similar_molecules('aspirine', threshold=0.5)
    new_search = time.time() - start

    print('\n' + '=' * 60)
    print('📋 COMPARAISON :')
    print(f"   Chargement   : Ancien {old_load:.2f}s → Optimisé {new_load:.2f}s ({'✅' if new_load < old_load else '❌'})")
    print(f"   Recherche    : Ancien {old_search:.3f}s → Optimisé {new_search:.3f}s ({'✅' if new_search < old_search else '❌'})")

    print('\n📊 STATISTIQUES DU CACHE :')
    stats = new_engine.get_cache_stats()
    print(f"   Cache mémoire: {stats['memory_cache_size']} entrées")
    print(f"   Cache disque : {stats['persistent_cache_size']} entrées")
    print(f"   Hit rate     : {stats['hit_rate']}")


if __name__ == '__main__':
    compare_performance()
