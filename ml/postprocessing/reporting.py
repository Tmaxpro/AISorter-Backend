import pandas as pd
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def build_json_report(df_sorted: pd.DataFrame, api_used: bool = False) -> Dict[str, Any]:
    """Construit le rapport JSON final"""
    
    # Remplacement des NaN par des valeurs par défaut
    logger.info("Remplacement des NaN par des valeurs par défaut...")
    df_clean = df_sorted.fillna({
        'hostname': 'Unknown',
        'ioc_type': 'Unknown',
        'description': 'No description',
        'feed_name': 'Unknown',
        'criticality_level': 'INFO'
    })
    
    # Calcul des statistiques
    logger.info("Calcul des statistiques...")
    summary = {
        "total_incidents": len(df_clean),
        "critical_count": len(df_clean[df_clean['criticality_level'] == 'CRITIQUE']),
        "high_count": len(df_clean[df_clean['criticality_level'] == 'ELEVE']),
        "medium_count": len(df_clean[df_clean['criticality_level'] == 'MOYEN']),
        "low_count": (len(df_clean[df_clean['criticality_level'] == 'FAIBLE']) + len(df_clean[df_clean['criticality_level'] == 'INFO'])),
        #"info_count": len(df_clean[df_clean['criticality_level'] == 'INFO'])
    }
    
    # Conversion des incidents en liste de dictionnaires
    logger.info("Conversion des incidents en liste de dictionnaires...")
    incidents = []
    for idx, row in df_clean.iterrows():
        incident = {
            "id": f"INC_{len(incidents)+1:06d}",
            "criticality_level": row.get('criticality_level', 'INFO'),
            "composite_score": round(float(row.get('composite_score', 0)), 3),
            "timestamp": datetime.now().isoformat(),
            "details": {
                "created_time": row.get('created_time', "Unknown"),
                "hostname": str(row.get('hostname', 'Unknown')),
                "internal_ip": str(row.get('internal_ip', 'Unknown')),
                "ioc_type": str(row.get('ioc_type', 'Unknown')),
                "ioc_value": str(row.get('ioc_value', 'Unknown')),
                "description": str(row.get('description', 'No description')),
                "feed_name": str(row.get('feed_name', 'Unknown')),
                "os_type": str(row.get('os_type', 'Unknown')),
            },
            "scores": {
                "criticality_score": round(float(row.get('final_criticality_score', 0)), 2),
                "contextual_score": round(float(row.get('contextual_score', 0)), 2),
                "ip_reputation_score": round(float(row.get('ip_reputation_score', 0)), 2)
            }
        }
        
        # Ajout des attributs réseau si disponibles
        network_attrs = {}
        for attr in ['ioc_attr_remote_ip', 'ioc_attr_direction', 'ioc_attr_remote_port']:
            if attr in row and pd.notna(row[attr]):
                network_attrs[attr.replace('ioc_attr_', '')] = str(row[attr])
        
        if network_attrs:
            incident["details"]["network"] = network_attrs
        
        incidents.append(incident)
    
    # Analytics
    logger.info("Calcul des analytics...")
    analytics = {
        "top_ioc_types": df_clean['ioc_type'].value_counts().head().to_dict(),
        "top_hosts": df_clean['hostname'].value_counts().head().to_dict(),
        "top_feeds": df_clean['feed_name'].value_counts().head().to_dict(),
        "criticality_distribution": df_clean['criticality_level'].value_counts().to_dict()
    }

    # Construction du rapport final
    logger.info("Construction du rapport final...")
    report = {
        #"_id": f"{uuid4()}",
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "incidents": incidents,
        "analytics": analytics,
        "metadata": {
            "total_processed": len(df_sorted),
            "api_used": api_used
        }
    }
    
    return report
