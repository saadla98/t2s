import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from database import init_db, SessionLocal
from services.data_pipeline import run_full_pipeline
from services.ml_service import train_all_models, train_module_classifier
from config import DATA_DIR, DATASET_FILENAME

def setup():
    print("Initialisation de la base de données...")
    init_db()
    
    db = SessionLocal()
    try:
        filepath = DATA_DIR / DATASET_FILENAME
        
        print(f"Importation des données depuis {filepath}...")
        result = run_full_pipeline(db, filepath)
        print(f"Import terminé : {result['records_imported']} enregistrements ajoutés.")
        
        print("Entraînement des modèles ML (Régression Logistique, Random Forest, XGBoost)...")
        ml_result = train_all_models(db)
        print(f"Meilleur modèle sélectionné : {ml_result['best_model']} (F1 Score: {ml_result['best_f1']})")
        
        print("Entraînement du modèle Expert (Prédiction du composant)...")
        expert_result = train_module_classifier(db)
        print(f"Modèle expert entraîné avec succès (Accuracy: {expert_result['accuracy']})")
        
        print("Initialisation terminée avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'initialisation: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup()
