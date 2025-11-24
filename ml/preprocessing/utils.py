def get_column_lists(df):
    """Retourne les listes de colonnes disponibles pour chaque type d'encodage"""
    available_cols = df.columns.tolist()
    
    cols_hash = [col for col in ['interface_ip', 'ioc_value', 'md5', 'process_id', 'process_name',
                                'process_path', 'process_unique_id', 'ioc_attr_local_ip', 
                                'ioc_attr_remote_ip', 'ioc_attr_dns_name', 'hostname', 'description', 'watchlist_name', 'feed_name'] if col in available_cols]
    
    cols_onehot = [col for col in ['os_type', 'ioc_type', 'ioc_attr_direction'] if col in available_cols]
    
    cols_label = [col for col in ['curt'] if col in available_cols]
    
    cols_numeric = [col for col in ['childproc_count', 'crossproc_count', 'filemod_count', 'modload_count',
                                   'netconn_count', 'regmod_count', 'segment_id', 'ioc_attr_local_port',
                                   'ioc_attr_port', 'ioc_attr_remote_port'] if col in available_cols]
    
    return cols_hash, cols_onehot, cols_label, cols_numeric
