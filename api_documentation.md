# API Documentation

Toutes les routes API sont exposées via **FastAPI** sur `http://localhost:8005`.
L'interface Swagger complète est disponible sur `/docs`.

## 1. Scanner Data API

### `GET /api/data/scanners`
Récupère la liste paginée et filtrée des scanners.
- **Query Params :**
  - `limit` (int, defaut=50) : Nombre max de résultats.
  - `search` (str, optionnel) : Filtre sur le `Device_ID`.
- **Response :**
  ```json
  {
    "total": 662,
    "scanners": [
      {
        "device_id": "CT-540-001",
        "age": 5,
        "maintenance_cost": 1500.5,
        ...
      }
    ]
  }
  ```

---

## 2. Machine Learning API

### `GET /api/ml/models`
Récupère les performances et métriques de tous les modèles ML en base.
- **Response :**
  ```json
  {
    "status": "success",
    "best_model": "Logistic Regression",
    "best_f1": 0.955,
    "models": [
      {
        "model_name": "Logistic Regression",
        "is_best": true,
        "accuracy": 0.9549,
        "f1_score": 0.9550,
        ...
      }
    ]
  }
  ```

### `POST /api/ml/train`
Déclenche le ré-entraînement de tous les modèles (Logistic Regression, Random Forest, XGBoost) avec validation croisée StratifiedKFold.
- **Response :** Retourne le même objet que `GET /api/ml/models`.

---

## 3. Prediction API

### `POST /api/predict/risk`
Estime le niveau de risque d'un scanner, calcule le score de santé, et génère une recommandation.
- **Request Body :**
  ```json
  {
    "scanner_data": {
      "Device_ID": "CT-123",
      "Age": 8,
      ...
    },
    "technician_name": "Jean Dupont",
    "technician_role": "technician"
  }
  ```
- **Response :**
  ```json
  {
    "prediction_id": 42,
    "predicted_risk": "High",
    "health_score": 25,
    "probabilities": {"Low": 5.2, "Medium": 15.1, "High": 79.7},
    "recommendation": {
      "title": "Alerte Critique",
      "message": "Intervention immédiate requise...",
      ...
    }
  }
  ```

### `GET /api/predict/history`
Récupère l'historique des prédictions passées.
- **Query Params :** `limit` (int, défaut=50).
- **Response :** Liste des prédictions sérialisées.

### `GET /api/predict/{prediction_id}/report.pdf`
Génère et télécharge le rapport PDF d'une prédiction existante.
- **Response :** Fichier binaire (application/pdf).

### `GET /api/predict/{prediction_id}/shap`
Génère les valeurs SHAP (explicabilité locale) pour une prédiction spécifique.
- **Query Params :** `model_name` (str, défaut="random_forest").
- **Response :** Dictionnaire des variables avec leurs impacts absolus.

---

## 4. Analytics API

### `GET /api/analytics/modules`
Distribution des modules défaillants.

### `GET /api/analytics/age-distribution`
Distribution des équipements par tranches d'âge.

### `GET /api/analytics/risk-by-age`
Niveau de risque croisé par tranches d'âge.

### `GET /api/analytics/risk-distribution`
Distribution absolue du nombre de scanners par niveau de risque.

### `GET /api/analytics/correlations`
Matrice de corrélation de Pearson entre les différentes caractéristiques de la base de données.
