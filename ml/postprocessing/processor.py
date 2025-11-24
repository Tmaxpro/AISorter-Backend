import pandas as pd
import numpy as np
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from core.config import settings
from .scoring import calculate_criticality_score, categorize_criticality
from .reporting import build_json_report

logger = logging.getLogger(__name__)

class IncidentProcessor:
    """
    Classe pour traiter les incidents déjà prédits et générer des rapports JSON
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le processeur d'incidents
        
        Args:
            api_key: Clé API AbuseIPDB (optionnelle)
        """
        self.api_key = api_key or settings.ABUSEIPDB_KEY
        
    def extract_incidents(self, X: pd.DataFrame, y_pred: np.ndarray) -> pd.DataFrame:
        """
        Extrait les incidents basés sur les prédictions
        
        Args:
            X: DataFrame original des données
            y_pred: Array des prédictions (0 ou 1)
            
        Returns:
            DataFrame contenant uniquement les incidents prédits
        """
        # Masque des incidents (label == 1)
        incident_mask = y_pred == True
        
        # Extraction des incidents prédits
        X_predicted_incidents = X[incident_mask].copy()
        
        # Suppression des colonnes techniques si elles existent
        columns_to_drop = ['hash_features']
        existing_columns = [col for col in columns_to_drop if col in X_predicted_incidents.columns]
        
        if existing_columns:
            df_incidents = X_predicted_incidents.drop(columns=existing_columns)
        else:
            df_incidents = X_predicted_incidents
            
        return df_incidents
    
    def generate_incident_report(self, X: pd.DataFrame, y_pred: np.ndarray) -> Dict[str, Any]:
        """
        Génère un rapport d'incidents complet en JSON
        
        Args:
            X: DataFrame original des données
            y_pred: Array des prédictions (0 ou 1)
            
        Returns:
            Dictionnaire JSON du rapport d'incidents
        """
        # 1. Extraction des incidents
        logger.info("Extraction des incidents prédits...")
        df_incidents = self.extract_incidents(X, y_pred)
        logger.info(f"Nombre d'incidents extraits: {len(df_incidents)}")
        
        if df_incidents.empty:
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_incidents": 0,
                    "critical_count": 0,
                    "high_count": 0,
                    "medium_count": 0,
                    "low_count": 0,
                    "info_count": 0
                },
                "incidents": [],
                "analytics": {
                    "top_ioc_types": {},
                    "top_hosts": {},
                    "top_feeds": {}
                }
            }
        
        # 2. Calcul des scores de criticité
        logger.info("Calcul des scores de criticité..")
        df_scored = calculate_criticality_score(df_incidents, self.api_key)
        df_final = categorize_criticality(df_scored)
        
        # 3. Tri par criticité et score
        logger.info("Tri des incidents par criticité et score composite...")
        df_sorted = df_final.sort_values(
            ['criticality_order', 'composite_score'], 
            ascending=[False, False]
        )
        
        # 4. Génération du rapport JSON
        logger.info("Génération du rapport JSON...")
        report = build_json_report(df_sorted, api_used=bool(self.api_key))
        logger.info(f"Rapport généré avec succes")
        return report

def generate_incident_report_json(X: pd.DataFrame, y_pred: np.ndarray, 
                                api_key: Optional[str] = None, 
                                output_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour générer un rapport d'incidents en JSON
    """
    processor = IncidentProcessor(api_key)
    report = processor.generate_incident_report(X, y_pred)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Rapport sauvegardé dans {output_file}")
    
    return report
