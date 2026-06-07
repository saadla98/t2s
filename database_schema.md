# Database Schema Documentation

La base de données est implémentée avec **SQLite** et **SQLAlchemy** comme ORM.
Le fichier de base de données se trouve dans `backend/ct_scanner.db`.

## 1. Table: `scanners`
**But :** Stocker l'inventaire des scanners CT, leurs caractéristiques techniques, et l'historique de leur télémétrie de maintenance.

| Colonne | Type | Description |
| :--- | :--- | :--- |
| `id` | `Integer` | Clé primaire (auto-incrémentée) |
| `device_id` | `String` | Identifiant unique métier (ex: CT-540-001) |
| `device_type` | `String` | Type d'équipement |
| `age` | `Integer` | Âge de l'équipement en années |
| `manufacturer` | `String` | Fabricant du scanner |
| `model` | `String` | Modèle spécifique |
| `maintenance_cost` | `Float` | Coût total de maintenance cumulé (€) |
| `downtime` | `Float` | Temps d'arrêt total (jours) |
| `maintenance_frequency` | `Integer` | Nombre d'interventions de maintenance préventive |
| `failure_event_count` | `Integer` | Nombre total de pannes historiques |
| `mtbf` | `Float` | Temps Moyen Entre Pannes (Mean Time Between Failures) |
| `failure_rate` | `Float` | Taux de panne moyen |
| `downtime_per_failure` | `Float` | Temps d'arrêt moyen par événement de panne |
| `maintenance_intensity` | `Float` | Indice d'intensité de maintenance |
| `historical_risk_index` | `Float` | Indice historique (obsolète pour le ML, conservé pour archive) |
| `affected_module` | `String` | Composant ou module le plus récemment affecté |

---

## 2. Table: `predictions`
**But :** Conserver un historique complet des prédictions générées par l'Intelligence Artificielle pour assurer la traçabilité et l'audit.

| Colonne | Type | Description |
| :--- | :--- | :--- |
| `id` | `Integer` | Clé primaire (auto-incrémentée) |
| `device_id` | `String` | Référence au scanner diagnostiqué (`scanners.device_id`) |
| `technician_name` | `String` | Nom de l'opérateur ayant demandé la prédiction |
| `technician_role` | `String` | Rôle de l'opérateur (ex: technician, manager) |
| `predicted_risk` | `String` | Résultat final de l'IA (`Low`, `Medium`, `High`) |
| `confidence` | `Float` | Niveau de confiance de la prédiction (%) |
| `health_score` | `Float` | Score de santé global calculé (0 à 100) |
| `recommendation` | `String` | Texte de la recommandation d'action générée |
| `features_json` | `Text` | Snapshot JSON complet des données d'entrée au moment T |
| `probabilities_json`| `Text` | Snapshot JSON de la distribution probabiliste (Softmax) |
| `created_at` | `DateTime` | Horodatage de la prédiction (Défaut: UTC now) |

---

## Relations
Bien que la table `predictions` ne contienne pas de clé étrangère stricte au sens SQL vers `scanners.id`, la colonne `predictions.device_id` sert de liaison logique vers `scanners.device_id` pour agréger l'historique d'un équipement spécifique. L'utilisation d'une liaison par `String` permet de conserver les prédictions même si le scanner est retiré de la table d'inventaire.
