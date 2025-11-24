import joblib
import os
from core.config import settings

def load_model():
    if not os.path.exists(settings.MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {settings.MODEL_PATH}")
    return joblib.load(settings.MODEL_PATH)
