import pandas as pd
import io
import joblib
from fastapi import UploadFile
from .loader import load_model
from ..preprocessing.cleaning import DataPreprocessor
from ..postprocessing.processor import generate_incident_report_json
from core.config import settings

# Load model once
try:
    model = load_model()
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    model = None

def predict_from_file(upload_file: UploadFile):
    """
    Prend un UploadFile (Excel ou CSV), lit le fichier, applique le prétraitement DataPreprocessor,
    vérifie et réordonne les colonnes, applique le modèle, retourne les prédictions.
    """
    model = load_model()

    if model is None:
        raise RuntimeError("Model is not loaded")

    filename = upload_file.filename.lower()
    content = upload_file.file.read()
    
    if filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(content))
    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        df = pd.read_excel(io.BytesIO(content))
    else:
        raise ValueError('Format de fichier non supporté (CSV, XLSX)')
        
    # Prétraitement prudent
    preprocessor_safe = DataPreprocessor()
    df_processed = preprocessor_safe.fit_transform(df)
    
    # Prédiction directe avec le pipeline complet
    preds = model.predict(df_processed)
    
    report = generate_incident_report_json(
        X=df_processed, 
        y_pred=preds, 
        api_key=settings.API_KEY
    )
    
    return report
