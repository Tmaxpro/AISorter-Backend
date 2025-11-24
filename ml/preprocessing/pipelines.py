from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction import FeatureHasher
from .transformers import to_list_of_str, combine_hash_columns

def create_preprocessing_pipeline():
    """Crée le pipeline de preprocessing complet"""
    
    # Pipeline pour les features hashées
    hash_pipeline = Pipeline([
        ('to_list', FunctionTransformer(to_list_of_str, validate=False)),
        ('combine', FunctionTransformer(combine_hash_columns, validate=False)),
        ('hasher', FeatureHasher(n_features=64, input_type='string'))
    ])
    
    # Pipeline pour one-hot encoding
    onehot_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    # Pipeline pour label encoding
    label_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('label', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
    ])
    
    # Pipeline pour features numériques
    numeric_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])
    
    return hash_pipeline, onehot_pipeline, label_pipeline, numeric_pipeline
