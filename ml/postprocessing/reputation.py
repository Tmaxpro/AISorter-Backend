import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def check_ip_reputation(ip: str, api_key: str, max_age_days: int = 90) -> float:
    """
    Vérifie la réputation d'une IP avec l'API AbuseIPDB
    
    Args:
        ip: Adresse IP à vérifier
        api_key: Clé API AbuseIPDB
        max_age_days: Période de vérification en jours
        
    Returns:
        Score de réputation entre 0 et 10
    """
    if not ip or pd.isna(ip) or not api_key:
        return 0
    
    try:
        url = 'https://api.abuseipdb.com/api/v2/check'
        headers = {
            'Accept': 'application/json',
            'Key': api_key
        }
        params = {
            'ipAddress': ip,
            'maxAgeInDays': str(max_age_days)
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json().get('data', {})
        
        # Conversion du score (0-100 → 0-10)
        abuse_score = min(data.get('abuseConfidenceScore', 0) / 10, 10)
        
        # Si whitelisted, score = 0
        if data.get('isWhitelisted', False):
            return 0
        
        # Bonus si nombreux rapports
        if data.get('totalReports', 0) > 5:
            abuse_score = min(abuse_score + 1, 10)
            
        return abuse_score
        
    except Exception as e:
        logger.warning(f"Erreur vérification IP {ip}: {e}")
        return 0
