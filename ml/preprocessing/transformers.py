import numpy as np
import pandas as pd

def to_list_of_str(X):
    return X.apply(lambda x: list(x) if isinstance(x, (list, np.ndarray)) else [str(x)], axis=1).values

def combine_hash_columns(X):
    df = pd.DataFrame(X)
    return df.astype(str).agg(list, axis=1).values

def add_hash_features(X):
    cols_hash = ['interface_ip', 'ioc_value', 'md5', 'process_id', 'process_name',
                 'process_path', 'process_unique_id', 'ioc_attr_local_ip',
                 'ioc_attr_remote_ip', 'ioc_attr_dns_name']
    available_cols = [col for col in cols_hash if col in X.columns]
    if available_cols:
        X = X.copy()
        X['hash_features'] = X[available_cols].astype(str).values.tolist()
    return X
