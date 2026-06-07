# Préparation Q&A Jury de Soutenance

Ce document contient 30 questions probables que le jury pourrait vous poser lors de votre soutenance, accompagnées de réponses professionnelles et structurées.

## Machine Learning & Data Science

**1. Q : Pourquoi avez-vous choisi la Régression Logistique comme modèle final plutôt que Random Forest ou XGBoost, souvent réputés plus performants ?**
**R :** Après avoir corrigé un biais de fuite de données (Target Leakage), la Régression Logistique multinomiale s'est révélée être le modèle le plus robuste sur ce jeu de données avec un F1-Score de 95.5%. Face à un dataset tabulaire aux relations relativement linéaires, un algorithme simple généralise souvent mieux que des arbres boostés (XGBoost) qui ont tendance à sur-apprendre (overfitting) sur des échantillons de taille modeste.

**2. Q : Qu'est-ce que le "Target Leakage" et comment l'avez-vous détecté ?**
**R :** Le Target Leakage, ou fuite de données, se produit lorsqu'une variable utilisée pour l'entraînement contient indirectement la réponse à prédire. J'ai remarqué que le Random Forest obtenait 100% de précision. J'ai alors analysé l'importance des variables et la corrélation de Pearson. J'ai découvert que la variable `Historical_Risk_Index` séparait parfaitement les classes de risque. Je l'ai supprimée pour obliger le modèle à apprendre des vraies métriques de maintenance (MTBF, Âge).

**3. Q : Avez-vous rencontré des problèmes de classes déséquilibrées (Imbalanced data) ?**
**R :** Notre dataset était relativement bien équilibré avec environ 220 échantillons par classe (Faible, Modéré, Élevé). Néanmoins, pour garantir la robustesse, j'ai utilisé une validation croisée stratifiée (`StratifiedKFold`) et le F1-Score pondéré (Weighted F1) comme métrique principale plutôt que la simple "Accuracy".

**4. Q : Comment avez-vous traité les variables catégorielles comme "Affected_Module" ?**
**R :** J'ai utilisé le `LabelEncoder` de Scikit-Learn pour encoder les modules en valeurs numériques. Bien que le `OneHotEncoder` soit souvent préférable pour les catégories nominales afin d'éviter une fausse relation d'ordre, la Régression Logistique a très bien réagi à cet encodage et son impact relatif (SHAP) reste logiquement mesuré.

**5. Q : Comment fonction l'approche SHAP implémentée dans votre application ?**
**R :** SHAP (SHapley Additive exPlanations) est issu de la théorie des jeux. Il calcule la contribution marginale de chaque variable à la prédiction finale, en considérant toutes les combinaisons possibles de variables. Cela permet de dire non seulement "Cette machine est à risque Élevé", mais surtout "Elle l'est principalement à cause de son MTBF très bas et de son âge".

**6. Q : Quelle est la différence entre Précision (Precision) et Rappel (Recall) dans votre contexte ?**
**R :** La Précision indique : "Parmi tous les scanners que le modèle a classés comme Risque Élevé, combien le sont vraiment ?" (Utile pour éviter de remplacer des pièces pour rien). Le Rappel indique : "Parmi tous les scanners qui sont réellement à Risque Élevé, combien le modèle a-t-il réussi à détecter ?" (Utile pour éviter une panne surprise fatale). Le F1-Score est la moyenne harmonique des deux.

**7. Q : Avez-vous normalisé vos données ? Pourquoi ?**
**R :** Oui, j'ai utilisé `StandardScaler` (moyenne à 0, écart-type à 1). C'est crucial car des variables comme le "Coût de Maintenance" sont de l'ordre des milliers d'euros, tandis que "l'Âge" est inférieur à 20. Sans normalisation, la Régression Logistique aurait accordé un poids disproportionné au coût simplement à cause de son échelle.

**8. Q : Que fait la fonction Softmax dans votre module de prédiction ?**
**R :** Dans le cas de la Régression Logistique multinomiale, la fonction Softmax convertit les scores bruts (logits) du modèle en une distribution de probabilités (somme égale à 1 ou 100%). C'est ce qui nous permet d'afficher des jauges de probabilités claires (ex: 80% Élevé, 15% Modéré, 5% Faible) dans l'interface utilisateur.

## Ingénierie Logicielle & Architecture

**9. Q : Pourquoi séparer le backend (FastAPI) et le frontend (Next.js) plutôt que de faire une application monolithique (ex: Django complet) ?**
**R :** La séparation des préoccupations (Séparation of Concerns). FastAPI est asynchrone, hyper rapide, et nativement conçu pour la Data Science en Python. Next.js (React) est parfait pour créer des interfaces utilisateur interactives et performantes. Cela permet aussi d'évoluer (scaler) indépendamment et de développer des applications mobiles branchées sur la même API plus tard.

**10. Q : Pourquoi Next.js 16 avec App Router ?**
**R :** L'App Router offre le rendu côté serveur (SSR) et les React Server Components. Bien que cette interface soit fortement orientée client (`use client`), cette architecture offre un meilleur référencement, un découpage en composants plus propre, et des temps de chargement optimisés par rapport à un React SPA (Single Page Application) classique.

**11. Q : Comment la base de données est-elle gérée ?**
**R :** J'utilise SQLite pour ce projet afin de faciliter le déploiement et la démonstration, associé à SQLAlchemy comme ORM (Object-Relational Mapping). L'ORM permet de manipuler les enregistrements comme des objets Python, protège nativement contre les injections SQL, et rendrait une migration vers PostgreSQL très facile dans le futur en changeant simplement la chaîne de connexion.

**12. Q : Comment le PDF est-il généré côté serveur ?**
**R :** J'utilise la bibliothèque `ReportLab` en Python. Au lieu de générer le PDF côté client via HTML-to-PDF, la génération serveur permet de garantir un rendu parfait, sécurisé, et indépendant du navigateur du client. Les données sont passées au `pdf_service.py` qui assemble le document dynamiquement avec les styles corporatifs.

**13. Q : Comment gérez-vous les erreurs et les valeurs manquantes envoyées depuis le formulaire ?**
**R :** Côté Frontend, les champs `Input` sont typés et possèdent l'attribut `required`. Côté Backend, FastAPI utilise `Pydantic` pour valider rigoureusement le schéma JSON entrant. J'ai également implémenté des convertisseurs sécurisés (`_safe_float`) lors de la génération PDF pour éviter que l'application ne crash si des données inattendues traversent.

**14. Q : Votre application utilise-t-elle TailwindCSS. Quels sont ses avantages ?**
**R :** Tailwind est un framework CSS utilitaire. L'avantage majeur est de pouvoir styliser les composants directement dans le JSX sans faire d'allers-retours avec des fichiers `.css`. De plus, il purge le CSS inutilisé lors de la compilation (build), rendant le bundle final extrêmement léger. Il facilite énormément l'implémentation de thèmes complexes ("Glassmorphism").

**15. Q : Quelles bibliothèques graphiques utilisez-vous et pourquoi ?**
**R :** J'utilise `Recharts` pour les graphiques (barres, courbes, pie) car il s'intègre parfaitement avec React et supporte le rendu responsive. Pour les animations UI (le panneau de résultat qui apparaît doucement), j'utilise `Framer Motion`, qui permet des transitions matérielles fluides avec très peu de code.

## Métier & Pertinence

**16. Q : Qu'est-ce que le Score de Santé (Health Score) et comment est-il calculé ?**
**R :** C'est un indicateur global entre 0 et 100 inventé pour fournir une lecture immédiate au technicien. Il part d'une base (85 pour Faible, 50 pour Modéré, 15 pour Élevé) puis est pondéré finement en utilisant l'inverse des probabilités retournées par le modèle ML. Plus la probabilité de panne élevée monte, plus le score chute précisément.

**17. Q : Quelle est la valeur ajoutée de votre module "Expert" ?**
**R :** Le modèle ML se contente de donner une classification. Le module expert joue le rôle du "cerveau humain" : il analyse la classification et ses probabilités pour générer une recommandation exploitable ("Action requise : Remplacement du tube à rayons X sous 48h"). C'est le passage de l'IA analytique à l'IA prescriptive.

**18. Q : Qui est l'utilisateur final de votre application ?**
**R :** Principalement les ingénieurs de maintenance biomédicale (les techniciens sur le terrain ou dans le centre de contrôle) et les gestionnaires de parc hospitalier, qui ont besoin de prévoir les budgets et les temps d'arrêt.

**19. Q : Pourquoi est-il si critique d'anticiper la panne d'un scanner CT ?**
**R :** Un CT scanner coûte très cher (parfois plus d'un million d'euros). S'il tombe en panne, non seulement l'hôpital perd de l'argent, mais surtout les diagnostics des patients sont retardés, ce qui a un impact vital direct. Remplacer préventivement une pièce critique (comme le tube radiogène) avant la casse évite des jours d'arrêt inopinés.

**20. Q : Est-ce que ce système pourrait remplacer les techniciens ?**
**R :** Non, il s'agit d'un "Système d'Aide à la Décision" (Decision Support System). Comme l'indique la note en bas du PDF généré, l'IA identifie des modèles complexes dans les données que l'humain ne peut pas voir instantanément, mais l'intervention, la validation finale et la réparation restent une expertise strictement humaine.

## Sécurité & Déploiement

**21. Q : Comment assureriez-vous la sécurité de cette application en production ?**
**R :** Actuellement, le système ne possède pas d'authentification robuste (Login simulé). En production, j'ajouterais un système JWT (JSON Web Tokens) via OAuth2. Je mettrais également l'application derrière un Reverse Proxy (Nginx) en HTTPS pour chiffrer les flux de données (surtout s'il y a des données de santé, soumises au RGPD/HIPAA).

**22. Q : Comment envisagez-vous le déploiement ?**
**R :** L'idéal serait de conteneuriser l'application avec Docker (un conteneur pour le Backend FastAPI, un pour le Frontend Next.js). Cela permettrait de les déployer facilement sur n'importe quel fournisseur Cloud (AWS ECS, Azure App Service) de manière standardisée.

**23. Q : Que se passe-t-il si deux techniciens génèrent des prédictions en même temps ?**
**R :** L'architecture asynchrone de FastAPI (avec Uvicorn) permet de gérer des milliers de requêtes concurrentes sans bloquer le processus principal. La base de données SQLite gère les locks correctement, bien qu'en production massive, PostgreSQL serait nécessaire pour la haute concurrence en écriture.

**24. Q : Comment mettriez-vous à jour le modèle ML dans le temps (Data Drift) ?**
**R :** Le phénomène de *Concept Drift* signifie que le modèle devient obsolète car les comportements des machines évoluent. L'application possède déjà une route `POST /api/ml/train`. On pourrait configurer un cron job (pipeline CI/CD) pour déclencher cet entraînement chaque mois sur les nouvelles données récoltées.

**25. Q : Pourquoi ne pas avoir utilisé une API ML as-a-Service (ex: AWS SageMaker) ?**
**R :** Intégrer Scikit-Learn directement dans notre backend FastAPI (In-House ML) nous donne le contrôle total sur la confidentialité des données (pas de fuite d'informations médicales vers un cloud tiers) et supprime les coûts de latence et de requêtes externes. Le modèle étant relativement léger, il tourne très rapidement sur un simple CPU.

## Difficultés & Bilan Personnel

**26. Q : Quelle a été la plus grande difficulté technique du projet ?**
**R :** Gérer les types stricts de TypeScript côté frontend lors de la réception des données complexes du backend Python, notamment pour le formatage des données pour les graphiques Recharts (ex: l'erreur de typage sur `Formatter`) et l'harmonisation du Target Leakage pour que le backend et l'IA soient en adéquation.

**27. Q : Qu'avez-vous appris sur la communication Backend-Frontend ?**
**R :** J'ai appris l'importance d'utiliser `Promise.all` pour fetcher plusieurs endpoints en parallèle (ex: sur la page Analytics) afin de ne pas ralentir le chargement de la page, et l'importance de bien gérer les états de chargement (`loading states`) pour l'expérience utilisateur (UX).

**28. Q : Si vous aviez eu un mois supplémentaire, qu'auriez-vous ajouté ?**
**R :** J'aurais ajouté des capteurs IoT simulés pour envoyer de la télémétrie en temps réel au backend via WebSockets. Le tableau de bord aurait ainsi mis à jour ses prédictions en direct au lieu d'attendre une saisie manuelle.

**29. Q : Êtes-vous satisfait du design de l'interface ? Comment avez-vous fait vos choix ?**
**R :** Oui, j'ai opté pour un mode sombre "Glassmorphism" avec des couleurs vibrantes (Bleu ciel, Émeraude) typiques des outils de cybersécurité et d'analyse High-Tech contemporains. C'est psychologiquement rassurant et professionnel pour des opérateurs qui passent la journée devant ces écrans.

**30. Q : En conclusion, quelle est la réussite majeure de votre PFE ?**
**R :** Avoir réussi à lier trois mondes souvent cloisonnés : la Data Science (ML pur), le Backend (Ingénierie de données robuste), et le Frontend (UI/UX design moderne), pour livrer un produit final de bout-en-bout, fonctionnel, documenté et prêt à l'emploi.
