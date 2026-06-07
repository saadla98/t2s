# Plateforme de Maintenance Prédictive T2S — Présentation

Le développement du système intelligent d'aide à la décision pour l'estimation du risque de panne des scanners CT (Application au GE Optima 540) est **terminé avec succès**.

La plateforme se compose d'un backend en Python/FastAPI propulsé par l'apprentissage automatique (Scikit-Learn, XGBoost) et d'un frontend en Next.js (React) avec une interface utilisateur moderne (TailwindCSS v4, Shadcn UI).

## Lancement de la plateforme

L'application tourne localement sur votre machine :
- **Frontend (Interface Utilisateur) :** [http://localhost:3005](http://localhost:3005)
- **Backend (API FastAPI) :** [http://localhost:8005/docs](http://localhost:8005/docs) (Swagger UI)

## Fonctionnalités Développées

### 1. Landing Page et Connexion
- **Page d'accueil :** Interface moderne (Dark Glassmorphism) présentant le projet PFE avec des animations (Framer Motion).
- **Portail de Connexion :** Formulaire de connexion décoratif avec gestion de rôles (`Technicien` vs `Responsable Maintenance`).

### 2. Tableau de Bord (`/dashboard`)
Vue d'ensemble en temps réel de votre parc matériel :
- Cartes d'indicateurs KPI (Scanners supervisés, Répartition des risques Faible/Modéré/Élevé).
- Moyennes globales du parc (Âge moyen, Temps d'arrêt moyen, MTBF, Coût de maintenance moyen).
- Graphique circulaire (Recharts) interactif montrant la distribution des risques.

### 3. Parc Scanners (`/scanners`)
- Tableau listant les 663 équipements de la base de données.
- Recherche instantanée par ID (ex: CT-540-001) ou par modèle.
- Badges de statut de risque colorés.

### 4. Prédiction IA (`/prediction`)
L'outil d'aide à la décision central pour les techniciens biomédicaux :
- Formulaire pour entrer la télémétrie du scanner (âge, coût, arrêt, fréquence des pannes, MTBF, etc.).
- Calcul du niveau de risque global avec distribution probabiliste visuelle.
- **Score de Santé (0-100)** accompagnant la prédiction.
- **Recommandations Intelligentes :** Actions suggérées générées dynamiquement en français selon le niveau de risque.
- **Génération PDF :** Bouton pour télécharger l'export PDF complet de l'analyse.

### 5. Analytiques EDA (`/analytics`)
Exploration visuelle du dataset initial :
- Fréquence de panne historique classée par module (Graphique à barres horizontales).
- Démographie du parc (Répartition par âge).
- Niveau de risque segmenté par groupe d'âge.

### 6. Modèles ML & SHAP (`/models`)
Pour la transparence des décisions (Explainable AI) :
- Tableau de comparaison des algorithmes entraînés (*Random Forest*, *Logistic Regression*, *XGBoost*).
- Métriques détaillées : Accuracy, Precision, Recall, F1 Score et scores de Validation Croisée.
- Top 10 des variables les plus importantes extraites via l'Analyse SHAP.

### 7. Module Expert (`/expert`)
*Bonus PFE implémenté :*
- Modèle classifieur secondaire (*Random Forest* dédié).
- Prédit le composant spécifique (parmi 7 catégories, ex: *Cooling / Tube*, *Detector / Sensors*) le plus susceptible d'être à l'origine de la panne imminente.

---

> [!TIP]
> Naviguez sur `http://localhost:3005` depuis votre navigateur web habituel (Chrome/Edge/Firefox) pour tester l'application complète en conditions réelles !
