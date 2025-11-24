import pandas as pd
import json
import socket
import struct
import logging
from sklearn.base import BaseEstimator, TransformerMixin

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor(BaseEstimator, TransformerMixin):
    """
    Classe pour le preprocessing sécurisé des données
    """
    
    def __init__(self):
        # Colonnes à supprimer si elles existent
        self.columns_to_drop = [
            'total_hosts', 'alert_severity', 'alert_type', 'comms_ip',
            'feed_id', 'feed_rating', 'group', 'ioc_confidence',
            'link', 'sha256', 'report_ignored', 'report_score',
            'sensor_criticality', 'sensor_id', 'status', 'unique_id',
            'watchlist_id', 'Unnamed: 0', 'labelisation', 'incident'
        ]
        
        # Colonnes à convertir en numérique
        self.numeric_conversion_cols = [
            'ioc_attr_local_ip',
            'ioc_attr_local_port',
            'ioc_attr_remote_port',
            'ioc_attr_port',
            'ioc_attr_remote_ip'
        ]

        self.expected_columns = [
            'childproc_count', 'created_time', 'crossproc_count', 'description',
            'feed_name', 'filemod_count', 'hostname', 'interface_ip', 'ioc_type',
            'ioc_value', 'md5', 'modload_count', 'netconn_count', 'os_type',
            'process_id', 'process_name', 'process_path', 'process_unique_id',
            'regmod_count', 'segment_id', 'watchlist_name', 'ioc_attr_direction',
            'ioc_attr_dns_name', 'ioc_attr_local_ip', 'ioc_attr_local_port',
            'ioc_attr_port', 'ioc_attr_protocol', 'ioc_attr_remote_ip','ioc_attr_remote_port'
       ]
    
    def parse_ioc_attr(self, row):
        """Parse la colonne ioc_attr de manière sécurisée"""
        try:
            if pd.isna(row.get('ioc_attr')):
                return row
            
            ioc_attr_str = str(row['ioc_attr'])
            
            # Nettoyer la chaîne si nécessaire
            if ioc_attr_str.startswith("b'") and ioc_attr_str.endswith("'"):
                ioc_attr_str = ioc_attr_str[2:-1]
            
            # Parser le JSON
            parsed_data = json.loads(ioc_attr_str)
            
            # Ajouter les nouvelles colonnes
            for key, value in parsed_data.items():
                row[f'ioc_attr_{key}'] = value
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # print(f"Erreur lors du parsing de ioc_attr: {e}")
            # En cas d'erreur, on continue sans ajouter les colonnes
            pass
        
        return row
    
    def int_to_ip(self, ip_int):
        """Convertit un entier en adresse IP"""
        try:
            if pd.isna(ip_int):
                return "0.0.0.0"
            ip_unsigned = int(ip_int) & 0xFFFFFFFF
            return socket.inet_ntoa(struct.pack("!I", ip_unsigned))
        except (ValueError, struct.error, OverflowError) as e:
            # print(f"Erreur conversion IP: {e}")
            return "0.0.0.0"
    
    def safe_drop_columns(self, df, columns_to_drop):
        """Supprime les colonnes de manière sécurisée"""
        existing_columns = [col for col in columns_to_drop if col in df.columns]
        if existing_columns:
            try:
                df = df.drop(existing_columns, axis=1)
                # print(f"Colonnes supprimées: {existing_columns}")
            except Exception as e:
                print(f"Erreur lors de la suppression des colonnes {existing_columns}: {e}")
        else:
            # print("Aucune colonne à supprimer trouvée")
            pass
        return df
    
    def fit(self, X, y=None):
        """Méthode fit requise par sklearn"""
        return self
    
    def transform(self, X):
        """Transformation principale des données"""
        df = X.copy()
        
        #print("=== Début du preprocessing ===")
        logging.info("Démarrage du preprocessing des données")
        
        # 1. Parsing de ioc_attr si la colonne existe
        if 'ioc_attr' in df.columns:
            try:
                #print("Parsing de la colonne ioc_attr...")
                logging.info("Parsing de la colonne ioc_attr")
                df = df.apply(self.parse_ioc_attr, axis=1)
                
                # Réorganiser les colonnes
                cols = [col for col in df.columns if not col.startswith('ioc_attr_')] + \
                       [col for col in df.columns if col.startswith('ioc_attr_')]
                df = df[cols]
                
                # Supprimer la colonne ioc_attr originale
                df = df.drop('ioc_attr', axis=1)
                #print("Parsing terminé avec succès")
                logging.info("Parsing de ioc_attr terminé avec succès")
            except Exception as e:
                #print(f"Erreur lors du parsing ioc_attr: {e}")
                logging.error(f"Erreur lors du parsing ioc_attr: {e}")
        
        # 2. Création de la target si les colonnes existent
        if 'labelisation' in df.columns and 'incident' in df.columns:
            try:
                df['target'] = df['labelisation'] & df['incident']
                #print("Colonne target créée")
                logging.info("Colonne target créée avec succès")
            except Exception as e:
                #print(f"Erreur lors de la création de target: {e}")
                logging.error(f"Erreur lors de la création de target: {e}")
        
        # 3. Conversion numérique sécurisée
        for col in self.numeric_conversion_cols:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                except Exception as e:
                    #print(f"Erreur conversion numérique pour {col}: {e}")
                    logging.error(f"Erreur conversion numérique pour {col}: {e}")
        
        # 4. Conversion IP sécurisée
        if 'ioc_attr_local_ip' in df.columns:
            try:
                df['ioc_attr_local_ip'] = df['ioc_attr_local_ip'].apply(self.int_to_ip)
                #print("Conversion ioc_attr_local_ip terminée")
                logging.info("Conversion ioc_attr_local_ip terminée")
            except Exception as e:
                #print(f"Erreur conversion local_ip: {e}")
                logging.error(f"Erreur conversion local_ip: {e}")
        
        if 'ioc_attr_remote_ip' in df.columns:
            try:
                df['ioc_attr_remote_ip'] = df['ioc_attr_remote_ip'].apply(self.int_to_ip)
                #print("Conversion ioc_attr_remote_ip terminée")
                logging.info("Conversion ioc_attr_remote_ip terminée")
            except Exception as e:
                #print(f"Erreur conversion remote_ip: {e}")
                logging.error(f"Erreur conversion remote_ip: {e}")
        
        # 5. Conversion watchlist_name en string
        if 'watchlist_name' in df.columns:
            try:
                df['watchlist_name'] = df['watchlist_name'].astype(str)
            except Exception as e:
                #print(f"Erreur conversion watchlist_name: {e}")
                logging.error(f"Erreur conversion watchlist_name: {e}")
        
        # 6. Suppression sécurisée des colonnes
        logging.info("Suppression des colonnes inutiles...")
        df = self.safe_drop_columns(df, self.columns_to_drop)

        # Entrinement
        if 'target' in df.columns:
            self.expected_columns.append('target')
        
        logging.info("Verification des colonnes attendues...")
        # Only keep columns that exist in df
        cols_to_keep = [col for col in self.expected_columns if col in df.columns]
        df = df[cols_to_keep]
        
        print("=== Preprocessing terminé ===")
        return df
