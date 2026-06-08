# Mises à jour du Projet — T2S Predict
> Contexte PFE : Système de prédiction du risque de panne pour scanners CT (GE Optima 540)

---

## 1. Intégration de données réelles GE Optima 540

### Pourquoi
Le dataset initial (`CT_Scanner_Dataset_Engineered_T2S_with_Affected_Module.csv`) était entièrement **synthétique** (662 lignes générées). Le modèle ne s'était jamais entraîné sur des interventions réelles, ce qui créait un écart important entre les performances en laboratoire et les performances en conditions réelles.

### Ce qu'on a fait
Deux nouvelles sources de données réelles ont été intégrées :

| Source | Format | Lignes | Niveau |
|--------|--------|--------|--------|
| `optima540_interventions_real_serials.csv` | CSV (`;`) | 49 | Par intervention |
| `optima540_scanners_real_serials.xlsx` | Excel | 11 | Par scanner (agrégé) |

**Mapping des colonnes :**
- `Component` → `Affected_Module` (ex: `DAS / cartes acquisition` → `DAS / Data Acquisition`)
- `Severity_Level` → `Failure_Risk` (Low / Medium / High — correspondance directe)
- `Business_Risk_Level` → `Failure_Risk` (pour le fichier Excel)
- Features agrégées calculées par `Serial_Number` : `MTBF`, `Failure_Rate`, `Downtime_Per_Failure`, `Maintenance_Intensity`
- `Age` et `Maintenance_Cost` : valeurs médianes du dataset synthétique (seules valeurs non disponibles dans les données réelles)

**Résultat :** Dataset fusionné `CT_Scanner_Dataset_Merged.csv` — **722 lignes** (662 + 49 + 11)

**Script :** `merge_datasets.py`

---

## 2. Évaluation du modèle sur données réelles (avant/après)

### Pourquoi
Avant d'intégrer les données réelles, on a d'abord évalué les performances du modèle existant sur ces données pour quantifier l'écart et justifier les améliorations.

### Résultats de l'évaluation initiale (modèle entraîné sur synthétique uniquement)

| Classe | Rappel (Recall) | Constat |
|--------|----------------|---------|
| Low    | 55%            | Passable |
| **Medium** | **13%**    | **Très mauvais** — prédit presque toujours "High" |
| High   | 87%            | Bon mais trop agressif |

**Accuracy globale : 44.9%** sur les 49 interventions réelles.

**Cause identifiée :** Le modèle était biaisé vers la classe "High" car les features agrégées par scanner (Failure_Rate élevé pour les scanners avec beaucoup d'interventions) poussaient systématiquement la prédiction vers le risque maximal.

**Script :** `evaluate_real_data.py` — génère `real_data_evaluation_results.csv`

---

## 3. Correction du biais de classe — Class Weights

### Pourquoi
Le modèle original ne prenait pas en compte le déséquilibre de classes. Après fusion, la distribution restait relativement équilibrée (236 Low / 245 Medium / 241 High), mais le pattern des données réelles créait un biais vers "High".

### Ce qu'on a fait
Modification de `backend/services/ml_service.py` :

- **Logistic Regression** : ajout de `class_weight="balanced"`
- **Random Forest** : ajout de `class_weight="balanced"`
- **XGBoost** : ajout de `sample_weight=compute_sample_weight("balanced", y_train)` lors du `.fit()`

### Impact

| Métrique | Avant | Après |
|----------|-------|-------|
| Accuracy (données réelles) | 44.9% | **71.4%** |
| Recall Medium | 13% | **70%** |
| Recall High | 87% | 80% |
| F1 global (test set) | 0.8643 | **0.8699** |

---

## 4. Correction des warnings de dépréciation

### Pourquoi
Des warnings apparaissaient à chaque entraînement, signalant des paramètres obsolètes qui seront supprimés dans de futures versions des bibliothèques.

### Ce qu'on a fait

| Bibliothèque | Paramètre supprimé | Raison |
|---|---|---|
| scikit-learn `LogisticRegression` | `multi_class="multinomial"` | Deprecated depuis sklearn 1.5 — comportement par défaut désormais |
| XGBoost `XGBClassifier` | `use_label_encoder=False` | Paramètre ignoré depuis XGBoost 1.6 |

---

## 5. Intégration du logo T2S dans l'interface

### Pourquoi
L'interface affichait un logo textuel générique ("T2S Predict"). Le logo officiel **Techniques Science Santé by T2S Group** renforce l'identité visuelle du projet.

### Ce qu'on a fait
- Fichier logo : `t2s_logo.png` copié dans `frontend/public/`
- Composant modifié : `frontend/src/components/layout/sidebar.tsx`
- Remplacement de l'icône + texte par un `<Image>` Next.js (106×68px)
- Filtre CSS `brightness-0 invert` pour adapter le logo au thème sombre de l'interface
- Dimensions corrigées pour respecter le ratio réel du logo (1024×661px → ratio 1.55:1)

---

## 6. Correction de la configuration API

### Pourquoi
L'URL de base de l'API dans le frontend pointait vers le port **8005** alors que le backend FastAPI tourne sur le port **8000**, causant une erreur `AxiosError: Network Error` sur toutes les pages.

### Ce qu'on a fait
Modification de `frontend/src/lib/api.ts` :
```diff
- const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8005/api";
+ const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
```

---

## Résumé des fichiers modifiés

| Fichier | Type de modification |
|---------|---------------------|
| `merge_datasets.py` | Nouveau script — fusion des 3 sources de données |
| `evaluate_real_data.py` | Nouveau script — évaluation sur données réelles |
| `CT_Scanner_Dataset_Merged.csv` | Nouveau dataset fusionné (722 lignes) |
| `backend/config.py` | `DATASET_FILENAME` → `CT_Scanner_Dataset_Merged.csv` |
| `backend/services/ml_service.py` | Class weights + suppression warnings |
| `frontend/src/lib/api.ts` | Port API 8005 → 8000 |
| `frontend/src/components/layout/sidebar.tsx` | Logo T2S intégré |
| `frontend/public/t2s_logo.png` | Nouveau fichier logo |
