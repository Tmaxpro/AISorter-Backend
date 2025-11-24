**Projet**
- **Nom**: Backend - Détection et classification d'incidents (ML)
- **Description**: Backend FastAPI pour la détection et la classification d'incidents à l'aide de modèles de machine learning. Fournit des endpoints pour prédire à partir d'un fichier uploadé, stocker les rapports dans MongoDB et consulter l'historique.

**Fonctionnalités**
- **Prédiction**: Endpoint `POST /predict` qui accepte un fichier (log, CSV, etc.) et renvoie un rapport JSON de détection/classification.
- **Historique**: Endpoint `GET /history` pour lister les rapports enregistrés.
- **Détails d'un rapport**: Endpoint `GET /history/{report_id}` pour récupérer un rapport par son identifiant.
- **Stockage**: Les rapports sont persistés dans une collection MongoDB.

**Architecture (haute-niveau)**
- **API**: `app/main.py` (FastAPI)
- **Base de données**: MongoDB via l'URL fournie dans les variables d'environnement.
- **ML**: Code de chargement et d'inférence dans `ml/model/` (`loader.py`, `predictor.py`).
- **Pré/post-processing**: `ml/preprocessing/` et `ml/postprocessing/` contiennent les traitements avant/après modèle.
- **Entraînement**: script d'entraînement dans `ml/model/training/training.py`.

**Structure du dépôt**
- **`app/`**: code de l'API et config DB (`main.py`, `database.py`).
- **`core/`**: configuration générale (`config.py`).
- **`ml/`**: modèle, entraînement, preprocessing, postprocessing.
- **`requirements.txt`**: dépendances Python.
- **`.env.exemple`**: exemple des variables d'environnement attendues.

**Prérequis**
- **Python**: 3.9+ recommandé.
- **MongoDB**: accessible depuis l'application (URI dans `MONGO_URL`).
- **Clés API**: si vous utilisez des services externes (ex. AbuseIPDB), ajouter dans l'`.env`.

**Installation (locale)**
- **Créer un venv**:
  - `python -m venv .venv`
  - `source .venv/bin/activate`
- **Installer les dépendances**:
  - `pip install -r requirements.txt`
- **Préparer les variables d'environnement**:
  - Copier `./.env.exemple` en `.env` puis remplir les valeurs.

**Variables d'environnement importantes**
- **`MONGO_URL`**: URI de connexion MongoDB.
- **`DB_NAME`**: nom de la base de données.
- **`COLLECTION_NAME`**: collection pour stocker les rapports.
- **`MODEL_PATH`**: chemin vers le modèle sérialisé si nécessaire.
- **`TRAINING_DATA_PATH`**: chemin des données d'entraînement.
- **`API_KEY`, `ABUSEIPDB_KEY`**: clés optionnelles pour services externes.

Référez-vous à `/.env.exemple` pour la liste complète.

**Exécution de l'API (développement)**
- **Commande**:
  - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Accès**:
  - API Root: `http://localhost:8000`
  - Documentation interactive (Swagger): `http://localhost:8000/docs`

**Exemples d'utilisation**
- **Envoyer un fichier pour prédiction (curl)**:
  - `curl -X POST "http://localhost:8000/predict" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@/chemin/vers/mon_fichier.log"`
- **Lister l'historique (curl)**:
  - `curl http://localhost:8000/history`
- **Récupérer un rapport par id (curl)**:
  - `curl http://localhost:8000/history/<report_id>`
- **Exemple Python (requests)**:
  - ````python
    import requests

    files = {'file': open('mon_fichier.csv','rb')}
    r = requests.post('http://localhost:8000/predict', files=files)
    print(r.json())
    ````

**Modèle & Entraînement**
- **Chargement / inférence**: voir `ml/model/loader.py` et `ml/model/predictor.py`.
- **Entraînement**: le script principal d'entraînement se trouve dans `ml/model/training/training.py`.
- **Conseil**: exécuter l'entraînement dans un environnement isolé et mettre à jour `MODEL_PATH` après export du modèle.

**Post-processing & Scoring**
- Les règles d'interprétation, scoring et génération de rapports se trouvent dans `ml/postprocessing/` (`processor.py`, `scoring.py`, `reporting.py`, `reputation.py`).

**Développement & tests**
- **Style**: respectez les conventions de code dans le dépôt.
- **Tests**: ajouter un dossier `tests/` et des tests unitaires pour `predictor`, `processor` et les endpoints.

**Déploiement**
- **Docker**: créer un `Dockerfile` basé sur `python:3.11-slim`, copier le code, installer `requirements.txt`, exposer le port 8000 et démarrer avec `uvicorn`.
- **Variables sensibles**: utilisez des variables d'environnement du runtime ou un secret manager.
- **Production**: restreindre CORS, ajouter authentification, monitorer les performances et la latence de la ML.

**Dépannage rapide**
- **Erreur de connexion MongoDB**: vérifier `MONGO_URL` et l'accessibilité réseau.
- **Problèmes de modèle**: vérifier que `MODEL_PATH` pointe vers un fichier valide et que les dépendances ML sont installées.
- **Timeouts**: pour fichiers volumineux, envisager un worker asynchrone ou découpage en tâches.

**Contribuer**
- **Processus**: forker, créer une branche, ouvrir une Pull Request avec une description claire.
- **Style**: ajouter des tests et mettre à jour la documentation si nécessaire.

**Contact & Acknowledgements**
- **Auteur**: mainteneur du dépôt (mettre vos coordonnées ici).
- **Fichiers utiles**: `app/main.py`, `app/database.py`, `ml/model/`, `ml/preprocessing/`, `ml/postprocessing/`.