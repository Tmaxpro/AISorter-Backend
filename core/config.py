import os

class Settings:
    # Relatif à la racine du projet : le modèle sera sauvegardé dans le dossier ml/model
    MODEL_PATH = str(os.getenv('MODEL_PATH'))
    API_KEY = str(os.getenv('API_KEY'))
    ABUSEIPDB_KEY = str(os.getenv('ABUSEIPDB_KEY'))
    MONGO_URL = str(os.getenv('MONGO_URL'))
    DB_NAME = str(os.getenv('DB_NAME'))
    COLLECTION_NAME = str(os.getenv('COLLECTION_NAME'))
    TRAINING_DATA_PATH = str(os.getenv('TRAINING_DATA_PATH'))
settings = Settings()
