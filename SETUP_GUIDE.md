# Guide d'installation — T2S Predict
> PC vierge (Windows) — aucun logiciel requis au préalable

---

## Étape 1 — Télécharger et installer les logiciels

### 1.1 Git
👉 https://git-scm.com/download/win  
→ Télécharger **"64-bit Git for Windows Setup"**  
→ Installer avec les options par défaut (tout "Next")

### 1.2 Python 3.13
👉 https://www.python.org/downloads/  
→ Cliquer sur **"Download Python 3.13.x"**  
→ ⚠️ **IMPORTANT** : Cocher **"Add Python to PATH"** avant de cliquer Install  
→ Cliquer **"Install Now"**

### 1.3 Node.js
👉 https://nodejs.org/  
→ Télécharger la version **LTS** (bouton vert à gauche)  
→ Installer avec les options par défaut

---

## Étape 2 — Cloner le projet

Ouvrir **PowerShell** ou **CMD** et taper :

```bash
git clone https://github.com/saadla98/t2s.git
cd t2s
```

---

## Étape 3 — Installer les dépendances backend (Python)

```bash
cd backend
pip install -r requirements.txt
pip install openpyxl
```

> ⏳ Durée : 2-5 minutes (télécharge scikit-learn, xgboost, etc.)

---

## Étape 4 — Initialiser la base de données

```bash
python init_system.py
```

> Crée la base SQLite et importe le dataset automatiquement.

---

## Étape 5 — Installer les dépendances frontend (Node.js)

Ouvrir un **nouveau** terminal :

```bash
cd t2s/frontend
npm install
```

> ⏳ Durée : 1-3 minutes

---

## Étape 6 — Lancer les deux serveurs

### Terminal 1 — Backend
```bash
cd t2s/backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 — Frontend
```bash
cd t2s/frontend
npm run dev
```

---

## Étape 7 — Entraîner les modèles ML (première fois uniquement)

Ouvrir le navigateur → **http://localhost:3000**  
→ Aller dans **"Modèles ML & SHAP"**  
→ Cliquer **"Entraîner les modèles"**  
→ Attendre 1-2 minutes

---

## Accès à l'application

| Service | URL |
|---------|-----|
| Frontend (app) | http://localhost:3000 |
| Backend (API) | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## En cas de problème

### "python n'est pas reconnu"
→ Réinstaller Python en cochant **"Add to PATH"**  
→ Ou taper `python3` au lieu de `python`

### "pip n'est pas reconnu"
```bash
python -m pip install -r requirements.txt
```

### Port déjà utilisé
```bash
# Changer le port frontend
npm run dev -- --port 3001
```
