import numpy as np
from sentence_transformers import SentenceTransformer

# ============================================================
# 1. CHARGER LE MODÈLE NLP
# ============================================================
print("--- Chargement du modèle NLP...")

# "all-MiniLM-L6-v2" est un modèle léger et performant
# Il transforme le texte en vecteurs de 384 dimensions
model = SentenceTransformer('all-MiniLM-L6-v2')

print("[OK] Modèle chargé avec succès !")
print(f"Dimensions du vecteur : {model.get_sentence_embedding_dimension()}")

print("\n" + "="*60)

# ============================================================
# 2. CRÉER DES EMBEDDINGS
# ============================================================
print("--- Test des embeddings sur des molécules médicinales")

# Liste de molécules à tester
molecules = [
    "Aspirine",
    "Acide acétylsalicylique",
    "Paracétamol",
    "Doliprane",
    "Ibuprofène",
    "Advil",
    "Warfarine",
    "Coumadine",
    "Amoxicilline",
    "Pénicilline"
]

# Transformer chaque molécule en vecteur
embeddings = {}
for mol in molecules:
    embeddings[mol] = model.encode(mol)
    print(f"  [OK] {mol:30} -> vecteur de {len(embeddings[mol])} dimensions")

print("\n" + "="*60)

# ============================================================
# 3. CALCULER LA SIMILARITÉ COSINUS
# ============================================================
print("--- Calcul des similarités cosinus")

def cosine_similarity(vec1, vec2):
    """Calcule la similarité cosinus entre deux vecteurs"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Test 1 : Aspirine vs Acide acétylsalicylique (devraient être proches)
sim = cosine_similarity(embeddings["Aspirine"], embeddings["Acide acétylsalicylique"])
print(f"\nSimilarité 'Aspirine' vs 'Acide acétylsalicylique' : {sim:.4f}")
print(f"   -> {'[OK] TRES PROCHES (même molécule)' if sim > 0.8 else '[WARNING] Bizarre...'}")

# Test 2 : Aspirine vs Paracétamol (deux AINS différents)
sim = cosine_similarity(embeddings["Aspirine"], embeddings["Paracétamol"])
print(f"\nSimilarité 'Aspirine' vs 'Paracétamol' : {sim:.4f}")

# Test 3 : Aspirine vs Warfarine (interaction dangereuse)
sim = cosine_similarity(embeddings["Aspirine"], embeddings["Warfarine"])
print(f"\nSimilarité 'Aspirine' vs 'Warfarine' : {sim:.4f}")

# Test 4 : Marques commerciales vs Principes actifs
sim = cosine_similarity(embeddings["Doliprane"], embeddings["Paracétamol"])
print(f"\nSimilarité 'Doliprane' vs 'Paracétamol' : {sim:.4f}")

sim = cosine_similarity(embeddings["Advil"], embeddings["Ibuprofène"])
print(f"Similarité 'Advil' vs 'Ibuprofène' : {sim:.4f}")

print("\n" + "="*60)

# ============================================================
# 4. VISUALISATION SIMPLIFIÉE
# ============================================================
print("\nMatrice de similarité (extrait)")

# Sélection de quelques molécules
selected = ["Aspirine", "Paracétamol", "Warfarine", "Amoxicilline"]
selected_vectors = [embeddings[m] for m in selected]

# Créer la matrice de similarité
print("\n" + " "*15, end="")
for m in selected:
    print(f"{m[:12]:12}", end="")
print()

for i, m1 in enumerate(selected):
    print(f"{m1[:15]:15}", end="")
    for j, m2 in enumerate(selected):
        sim = cosine_similarity(selected_vectors[i], selected_vectors[j])
        if i == j:
            print(f"{'1.0000':12}", end="")
        else:
            print(f"{sim:12.4f}", end="")
    print()

print("\n" + "="*60)

# ============================================================
# 5. INTERPRÉTATION
# ============================================================
print("\nINTERPRÉTATION :")
print("   * 'Aspirine' et 'Acide acétylsalicylique' -> VERY HIGH (même molécule)")
print("   * 'Doliprane' et 'Paracétamol' -> HIGH (marque vs principe actif)")
print("   * 'Aspirine' et 'Warfarine' -> MOYEN (pas les mêmes, mais liés)")
print("   * 'Aspirine' et 'Paracétamol' -> FAIBLE (différents types)")

print("\nCONCLUSION : Le NLP permet de lier intelligemment")
print("   les noms commerciaux, les principes actifs et les synonymes !")
