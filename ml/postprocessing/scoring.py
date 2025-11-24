import pandas as pd
import numpy as np
from .reputation import check_ip_reputation

def calculate_criticality_score(df_incidents: pd.DataFrame, api_key: str = None) -> pd.DataFrame:
    """
    Calcule un score de criticité complet combinant multiples facteurs
    """
    df = df_incidents.copy()
    
    # Initialisation des scores
    df['criticality_score'] = 0.0
    df['contextual_score'] = 0.0
    df['ip_reputation_score'] = 0.0
    
    ## 1. Score basé sur le type d'IOC
    ioc_severity = {
        'md5': 15, 'sha1': 15, 'sha256': 15,  # Hash de fichier malveillant
        'domain': 12,                          # Domaine malveillant
        'ipv4': 10, 'ip': 10,                 # IP malveillante
        'dns': 8,                             # Requête DNS suspecte
        'registry': 7,                        # Modification registre
        'process': 6,                         # Processus suspect
        'file': 5,                           # Fichier suspect
        'network': 4,                        # Activité réseau
        'url': 3,                           # URL suspecte
        'query': 3                          # Requête suspecte
    }
    
    # Application du score IOC
    if 'ioc_type' in df.columns:
        for ioc_type, score in ioc_severity.items():
            mask = df['ioc_type'].str.contains(ioc_type, case=False, na=False)
            df.loc[mask, 'criticality_score'] += score
        
        # Score par défaut pour les types non listés
        known_types_regex = '|'.join(ioc_severity.keys())
        unknown_mask = ~df['ioc_type'].str.contains(known_types_regex, case=False, na=False)
        df.loc[unknown_mask, 'criticality_score'] += 2
    
    ## 2. Score basé sur l'activité système
    activity_weights = {
        'netconn_count': 1.8,
        'filemod_count': 2.2,
        'regmod_count': 2.0,
        'childproc_count': 1.7,
        'crossproc_count': 1.6,
        'modload_count': 1.3
    }
    
    for col, weight in activity_weights.items():
        if col in df.columns:
            df['criticality_score'] += np.log1p(df[col].fillna(0)) * weight
    
    ## 3. Score contextuel (menaces connues)
    critical_keywords = {
        'ransomware': 12, 'apt': 10, 'c2': 10, 'command and control': 10,
        'trojan': 9, 'backdoor': 9, 'malware': 8, 'exploit': 7,
        'phishing': 6, 'unusual': 5, 'suspicious': 4
    }
    
    if 'description' in df.columns:
        for keyword, score in critical_keywords.items():
            mask = df['description'].str.contains(keyword, case=False, na=False)
            df.loc[mask, 'contextual_score'] += score
    
    ## 4. Score des feeds de menace
    feed_weights = {
        'SANS': 10, 'AlienVault': 9, 'MalwareDomainList': 8,
        'Abuse.ch': 10, 'FireEye': 9, 'CrowdStrike': 8,
        'VirusTotal': 7, 'ThreatConnect': 8
    }
    
    if 'feed_name' in df.columns:
        df['feed_score'] = df['feed_name'].apply(
            lambda x: feed_weights.get(str(x), 5) if pd.notna(x) else 5
        )
        df['contextual_score'] += df['feed_score']
    
    ## 5. Vérification réputation IP
    ip_columns = ['ioc_attr_remote_ip', 'remote_ip', 'src_ip', 'dst_ip']
    for col in ip_columns:
        if col in df.columns:
            ip_mask = df[col].notna()
            if ip_mask.any():
                df.loc[ip_mask, 'ip_reputation_score'] = df.loc[ip_mask, col].apply(
                    lambda ip: check_ip_reputation(ip, api_key)
                )
                df['contextual_score'] += df['ip_reputation_score']
    
    ## 6. Facteurs environnementaux
    # Direction du trafic
    if 'ioc_attr_direction' in df.columns:
        outbound_mask = df['ioc_attr_direction'].str.contains('outbound|out', case=False, na=False)
        inbound_mask = df['ioc_attr_direction'].str.contains('inbound|in', case=False, na=False)
        df.loc[outbound_mask, 'contextual_score'] += 4
        df.loc[inbound_mask, 'contextual_score'] += 2
    
    # Ports suspects
    suspicious_ports = [22, 23, 135, 139, 445, 1433, 3389, 5985, 5986]
    port_columns = ['ioc_attr_local_port', 'ioc_attr_remote_port', 'ioc_attr_port']
    
    for port_col in port_columns:
        if port_col in df.columns:
            mask_suspicious = df[port_col].isin(suspicious_ports)
            df.loc[mask_suspicious, 'contextual_score'] += 3
    
    # OS ciblé
    if 'os_type' in df.columns:
        windows_mask = df['os_type'].str.contains('windows', case=False, na=False)
        df.loc[windows_mask, 'contextual_score'] *= 1.3
    
    # Heures de création des incidents
    # Bonus pour incidents nocturnes (22h-6h)
    if 'created_time' in df.columns:
        df['hour'] = pd.to_datetime(df['created_time']).dt.hour
        night_mask = (df['hour'] >= 22) | (df['hour'] <= 6)
        df.loc[night_mask, 'contextual_score'] *= 1.2
    
    ## 7. Normalisation et score composite
    # Normalisation min-max
    if df['criticality_score'].max() > df['criticality_score'].min():
        df['criticality_norm'] = (df['criticality_score'] - df['criticality_score'].min()) / \
                               (df['criticality_score'].max() - df['criticality_score'].min())
    else:
        df['criticality_norm'] = 0.5
        
    if df['contextual_score'].max() > df['contextual_score'].min():
        df['contextual_norm'] = (df['contextual_score'] - df['contextual_score'].min()) / \
                              (df['contextual_score'].max() - df['contextual_score'].min())
    else:
        df['contextual_norm'] = 0.5
    
    # Score composite pondéré
    df['composite_score'] = (df['criticality_norm'] * 0.7) + (df['contextual_norm'] * 0.3)

    df['final_criticality_score'] = df['criticality_score'] + df['contextual_score']
    df['final_criticality_score'] = df['final_criticality_score'].clip(upper=100)
    
    return df

def categorize_criticality(df: pd.DataFrame) -> pd.DataFrame:
    """Catégorise les incidents en niveaux de criticité"""
    conditions = [
        (df['composite_score'] >= 0.8),
        (df['composite_score'] >= 0.6),
        (df['composite_score'] >= 0.4),
        (df['composite_score'] >= 0)
    ]
    
    choices = ['CRITIQUE', 'ELEVE', 'MOYEN', 'FAIBLE']
    
    df['criticality_level'] = np.select(conditions, choices, default='INFO')
    df['criticality_order'] = df['criticality_level'].map({
        'CRITIQUE': 4, 'ELEVE': 3, 'MOYEN': 2, 'FAIBLE': 1, 'INFO': 0
    })
    
    return df
