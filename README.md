# AISorter Backend

Ce dépôt contient le backend de l'application **AISorter**, une solution de détection et de classification d'incidents de sécurité basée sur le Machine Learning. Il expose une API REST développée avec **FastAPI** qui permet d'analyser des fichiers de logs (CSV/Excel), de prédire la nature des incidents et de générer des rapports détaillés.

Le frontend de l'application est disponible ici : [AISorter Frontend](https://github.com/Tmaxpro/AISorter-Frontend)

## 🚀 Fonctionnalités

- **API REST performante** : Construite avec FastAPI pour une réponse rapide et une documentation automatique.
- **Analyse de fichiers** : Supporte l'upload de fichiers `.csv` et `.xlsx` pour l'analyse.
- **Pipeline Machine Learning** :
  - **Prétraitement** : Nettoyage et transformation des données brutes.
  - **Prédiction** : Classification des incidents à l'aide d'un modèle Scikit-learn entraîné.
  - **Post-traitement** : Génération de rapports d'incidents enrichis.
- **Enrichissement des données** : Intégration avec des services tiers (ex: AbuseIPDB) pour la réputation des IP.
- **Historique** : Stockage des rapports d'analyse dans une base de données **MongoDB**.

## 📂 Structure du Projet

```
backend/
├── app/
│   ├── main.py          # Point d'entrée de l'API (Routes /predict, /history)
│   ├── database.py      # Connexion à MongoDB
│   └── ...
├── core/
│   ├── config.py        # Gestion des variables d'environnement
│   └── ...
├── ml/
│   ├── model/           # Logique de chargement du modèle et prédiction
│   ├── preprocessing/   # Pipelines de nettoyage des données
│   ├── postprocessing/  # Génération de rapports et scoring
│   └── ...
├── requirements.txt     # Dépendances Python
└── README.md            # Documentation du projet
```

## 🛠️ Prérequis

- **Python 3.10+**
- **MongoDB** (Local ou Atlas)
- Clés API pour les services externes (si applicable, ex: AbuseIPDB, OpenAI/LLM pour les rapports).

## 📦 Installation

1. **Cloner le dépôt**

   ```bash
   git clone https://github.com/Tmaxpro/AISorter-Backend.git
   cd AISorter-Backend
   ```

2. **Créer un environnement virtuel**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**

   Créez un fichier `.env` à la racine du projet en vous basant sur les variables nécessaires (voir `core/config.py`) :

   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=aisorter_db
   COLLECTION_NAME=reports
   MODEL_PATH=ml/model/trained_model.pkl
   TRAINING_DATA_PATH=ml/model/training/training_data/
   API_KEY=votre_api_key_llm
   ABUSEIPDB_KEY=votre_cle_abuseipdb
   ```

## ▶️ Démarrage

Pour lancer le serveur de développement :

```bash
uvicorn app.main:app --reload
```

L'API sera accessible à l'adresse : `http://127.0.0.1:8000`

## 📚 Documentation de l'API

Une fois le serveur lancé, la documentation interactive est disponible automatiquement :

- **Swagger UI** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc** : [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Endpoints Principaux

- `POST /predict` : Upload d'un fichier pour analyse et génération de rapport.
- `GET /history` : Récupère la liste des analyses précédentes.
- `GET /history/{report_id}` : Récupère les détails d'un rapport spécifique.

## 🧠 Machine Learning

Le dossier `ml/` contient toute la logique métier liée à l'IA :

1. **Preprocessing** : Les données entrantes sont nettoyées (`cleaning.py`) et transformées pour correspondre au format attendu par le modèle.
2. **Modèle** : Le modèle (`predictor.py`) effectue la classification des incidents.
3. **Postprocessing** : Les résultats bruts sont transformés en un rapport JSON structuré, enrichi avec des scores de réputation et des explications (`processor.py`, `reputation.py`).

### Entraînement du Modèle

Le script d'entraînement se trouve dans `ml/model/training/training.py`. Il utilise un algorithme **Random Forest Classifier** optimisé pour la classification d'incidents.

**Processus d'entraînement :**

1. **Chargement des données** : Les données d'entraînement sont chargées depuis le chemin spécifié dans `TRAINING_DATA_PATH`.
2. **Prétraitement** :
   - Nettoyage initial via `DataPreprocessor`.
   - Génération de features (ex: hachage).
   - Transformation des colonnes (OneHotEncoding, LabelEncoding, StandardScaling) via un `ColumnTransformer`.
3. **Pipeline** : Un pipeline Scikit-learn intègre toutes les étapes de transformation et le classifieur final.
4. **Évaluation** :
   - Split Train/Test (80/20).
   - Validation croisée (Stratified K-Fold, 5 splits) pour assurer la robustesse.
   - Métriques suivies : Accuracy, Precision, Recall, F1-score, ROC-AUC.
5. **Sauvegarde** : Le modèle final, entraîné sur l'ensemble des données, est sauvegardé au format `.pkl` (Joblib).

Pour lancer un réentraînement manuel :

```bash
python -m ml.model.training.training
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une Pull Request.