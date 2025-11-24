import joblib
import pandas as pd
import numpy as np
from core.config import settings
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from ml.preprocessing.cleaning import DataPreprocessor
from ml.preprocessing.pipelines import create_preprocessing_pipeline
from ml.preprocessing.utils import get_column_lists
from ml.preprocessing.transformers import add_hash_features

MODEL_PATH = settings.MODEL_PATH

def main():
    """Fonction principale d'exécution"""
    try:
        # Charger les données (chemin relatif au fichier de script)
        print("Chargement des données...")
        #base_dir = Path(__file__).resolve().parent
        training_file = Path(settings.TRAINING_DATA_PATH)
        if not training_file.exists():
            raise FileNotFoundError(f"Fichier d'entraînement introuvable: {training_file}")
        df = pd.read_excel(training_file)
        print(f"Données chargées: {df.shape} (depuis {training_file})")
        
        # Appliquer le preprocessing initial
        data_preprocessor = DataPreprocessor()
        df_processed = data_preprocessor.fit_transform(df)
        
        # Vérifier si target existe, sinon l'utiliser comme variable à prédire
        if 'target' in df_processed.columns:
            y = df_processed['target']
            X = df_processed.drop('target', axis=1)
        else:
            print("Attention: colonne 'target' non trouvée!")
            return
        
        # Diviser les données
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )
        
        # Obtenir les listes de colonnes disponibles
        cols_hash, cols_onehot, cols_label, cols_numeric = get_column_lists(X)
        
        print(f"Colonnes hash: {len(cols_hash)}")
        print(f"Colonnes onehot: {len(cols_onehot)}")
        print(f"Colonnes label: {len(cols_label)}")
        print(f"Colonnes numeric: {len(cols_numeric)}")
        
        # Créer les pipelines
        hash_pipeline, onehot_pipeline, label_pipeline, numeric_pipeline = create_preprocessing_pipeline()
        
        # Créer le preprocessor avec gestion des colonnes vides
        transformers = []
        cols_hash_unique = ['hash_features'] if cols_hash else []
        if cols_hash_unique:
            transformers.append(('hash', hash_pipeline, cols_hash_unique))
        if cols_onehot:
            transformers.append(('onehot', onehot_pipeline, cols_onehot))
        if cols_label:
            transformers.append(('label', label_pipeline, cols_label))
        if cols_numeric:
            transformers.append(('num', numeric_pipeline, cols_numeric))
        
        if not transformers:
            print("Aucune colonne trouvée pour le preprocessing!")
            return
            
        preprocessor = ColumnTransformer(transformers=transformers)
        
        # Pipeline final AUTONOME avec ajout de hash_features
        final_pipeline = Pipeline([
            ('add_hash', FunctionTransformer(add_hash_features)),
            ('preprocessing', preprocessor),
            ('classifier', RandomForestClassifier(
                n_estimators=300, 
                class_weight={0: 0.583, 1: 3.16}, 
                random_state=42
            ))
        ])
        
        # Entraînement et évaluation
        print("Entraînement du modèle...")
        final_pipeline.fit(X_train, y_train)
        
        # Prédictions
        y_pred = final_pipeline.predict(X_test)
        
        # Métriques
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='binary', zero_division=0)
        rec = recall_score(y_test, y_pred, average='binary', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        print("=== Résultats de l'évaluation ===")
        print("Matrice de confusion:")
        print(cm)
        
        print(f"\n===== Résultats Random Forest =====")
        print(f"Accuracy  : {acc:.3f}")
        print(f"Precision : {prec:.3f}")
        print(f"Recall    : {rec:.3f}")
        print(f"F1-score  : {f1:.3f}")
        
        # Validation croisée
        print("\nValidation croisée...")
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        results = cross_validate(
            final_pipeline, X, y, cv=cv,
            scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc'],
            return_train_score=True
        )
        
        for metric in results:
            print(f"{metric}: {np.mean(results[metric]):.4f} ± {np.std(results[metric]):.4f}")
        
        #Entrainement final sur l'ensemble complet
        print("Entraînement final du modèle sur l'ensemble complet...")
        final_pipeline.fit(X, y)

        # Sauvegarder le modèle dans le chemin configuré
        print("Sauvegarde du modèle...")
        model_path = Path(settings.MODEL_PATH)
        # Créer le répertoire cible si nécessaire
        if not model_path.parent.exists():
            model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(final_pipeline, str(model_path))
        print(f"Modèle sauvegardé: {model_path}")
        
    except Exception as e:
        print(f"Erreur dans main(): {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()