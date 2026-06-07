# Guide de Présentation PFE (Soutenance)

Ce document est structuré pour vous aider à préparer votre présentation orale devant le jury pour le projet "T2S Predictive Maintenance Platform".

---

## 1. Contexte et Problématique (Problem Statement)
**Points clés :**
- L'industrie médicale s'appuie massivement sur des équipements lourds comme les scanners CT (Tomodensitométrie).
- Une panne imprévue engendre des retards de diagnostic pour les patients et des coûts exorbitants de réparation d'urgence.
- **Problématique :** Comment passer d'une maintenance réactive (on répare quand c'est cassé) ou préventive aveugle (on remplace à intervalle fixe) à une **maintenance prédictive**, ciblée, et intelligente ?

## 2. Objectifs du Projet
- Construire une plateforme logicielle complète (Fullstack Next.js + FastAPI) d'aide à la décision.
- Intégrer un moteur d'Intelligence Artificielle capable de classer le risque de panne d'un scanner (Faible, Modéré, Élevé).
- Fournir un système "Explainable AI" (IA Explicable) pour que le technicien comprenne *pourquoi* la machine a pris cette décision.
- Générer des rapports automatiques exportables (PDF).

## 3. Description du Dataset
- **Volume :** Base de données synthétisée et modélisée spécifiquement pour le contexte T2S (662 équipements).
- **Caractéristiques :** 20 colonnes incluant l'Âge, le Coût de maintenance, le MTBF (Mean Time Between Failures), le Taux de panne, les temps d'arrêt, et les modules historiquement affectés.
- **Cible (Target) :** `Failure_Risk` (Low, Medium, High).

## 4. Pré-traitement et Ingénierie des Variables (Data & Feature Engineering)
- Nettoyage des données, traitement des valeurs nulles.
- Encodage des variables catégorielles avec `LabelEncoder` (ex: `Affected_Module`).
- Normalisation des valeurs numériques par `StandardScaler` pour équilibrer le poids des variables dans les modèles (ex: Coût en milliers vs Âge en unités).
- **Point crucial (Résolution du Target Leakage) :** Lors de l'ingénierie initiale, une variable (`Historical_Risk_Index`) corrélait parfaitement à 100% avec le risque futur. Ce *leakage* a été identifié et supprimé afin de forcer le modèle à apprendre des vraies corrélations physiques (Temps d'arrêt, Fréquence de pannes).

## 5. Entraînement et Comparaison des Modèles
**Processus :** Validation Croisée Stratifiée (Stratified 5-Fold) pour assurer la robustesse.
- **Modèles testés :** Régression Logistique (Multinomiale), Random Forest, XGBoost.
- **Sélection Finale :** La *Régression Logistique* l'a emporté avec **95.5% de F1-Score**, surclassant les arbres de décision sur ce dataset post-leakage. Elle offre la meilleure généralisation.

## 6. L'IA Explicable (Explainable AI - SHAP)
- **Objectif :** Éviter l'effet "Boîte Noire".
- **Méthodologie :** Implémentation des valeurs de Shapley (SHAP) pour mesurer l'impact marginal de chaque paramètre.
- Les résultats montrent que le **Nombre d'Événements de Panne**, la **Fréquence de Maintenance** et l'**Âge** sont les indicateurs clés.

## 7. Le Module Expert et l'Architecture de l'Application
- **Expert Module :** Traduit la distribution probabiliste en règles métiers. Si la probabilité d'un risque élevé dépasse un seuil, il déclenche des alertes critiques avec des actions recommandées.
- **Architecture :** 
  - *Frontend :* Next.js 16 (App Router), TailwindCSS, Recharts, Framer Motion (Design premium, animations micro-interactions).
  - *Backend :* FastAPI (Python), Scikit-Learn pour le ML, ReportLab pour le PDF.
  - *BDD :* SQLite avec SQLAlchemy ORM.

## 8. Workflow de Démonstration (À exécuter devant le Jury)
1. **Landing & Login :** Montrer le design moderne.
2. **Dashboard :** Présenter les KPIs dynamiques (Scanners Actifs, Risques critiques).
3. **Exploration EDA (Analytics) :** Montrer la Matrice de Corrélation et la répartition des pannes pour prouver que les données ont été analysées.
4. **Modèles ML :** Montrer le tableau de comparaison et l'importance SHAP. Insister sur le fait que le "Meilleur modèle" est sélectionné automatiquement.
5. **Prédiction :** Utiliser l'auto-complétion pour sélectionner un scanner risqué. Générer le résultat.
6. **Résultat :** S'attarder sur le Score de Santé, les probabilités, la recommandation de l'expert.
7. **Export PDF :** Télécharger le PDF et l'ouvrir pour montrer que la chaîne de valeur est complète jusqu'au rapport livrable.

## 9. Conclusion et Améliorations Futures
- **Conclusion :** Le projet dépasse la simple preuve de concept ML. C'est un produit logiciel industriel, packagé, sécurisé, et prêt à l'emploi.
- **Futur :** Intégration de séries temporelles (LSTM) pour analyser les flux IoT continus (température du tube en direct), déploiement sur le Cloud (Docker/AWS).
