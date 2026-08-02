# SafeRx - Système Intelligent de Détection des Interactions Médicamenteuses

Ce projet est réalisé dans le cadre d'un stage de 3ème année (1ère année cycle ingénieur EMSI) au sein de l'équipe **SmartRx** (Cegedim).

## 🚀 Objectif du Projet
Développer un module intelligent capable d'alerter le pharmacien en temps réel en cas d'incompatibilité entre deux médicaments ou entre un médicament et les allergies/antécédents d'un patient. Le système utilise des techniques de **Recherche Sémantique (NLP - Embeddings)** pour lier intelligemment les substances actives et les contre-indications.

---

## 📁 Structure du Projet

```text
C:/projet_stage/
│
├── app.py                 # Application principale Streamlit (Interface Web et logique)
│
├── database/              # Dossier de base de données
│   ├── db_manager.py      # Script de création et de gestion de la base SQLite
│   └── database.db        # Base de données SQLite (générée automatiquement)
│
├── ai/                    # Moteur d'IA & Traitement du Langage (NLP)
│   └── ai_engine.py       # Algorithmes d'embeddings et de similarité sémantique
│
├── data/                  # Fichiers de données initiaux
│   ├── products.csv       # Liste simulée de médicaments et principes actifs
│   └── patients.json      # Liste simulée de profils patients
│
└── requirements.txt       # Dépendances (streamlit, sentence-transformers, pandas, sqlite3, etc.)
```

---

## 🛠️ Technologies Utilisées
* **Interface Web :** Streamlit (Framework Python moderne pour applications Data/IA)
* **IA / NLP :** Sentence-Transformers (Hugging Face), Scikit-learn (similarité cosinus)
* **Base de données :** SQLite / Pandas
* **Langage :** Python 3.x
