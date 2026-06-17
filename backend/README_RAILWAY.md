# Déployer le backend sur Railway (via GitHub)

Ce dossier `backend/` est prêt à être déployé sur **Railway**. Railway lit ton
repo GitHub, détecte Python (Nixpacks), installe `requirements.txt` et lance
l'API avec la commande définie dans `railway.json` / `Procfile`.

## Fichiers de déploiement (déjà présents)

| Fichier            | Rôle                                                        |
|--------------------|-------------------------------------------------------------|
| `requirements.txt` | dépendances Python                                          |
| `railway.json`     | builder + commande de démarrage + healthcheck `/`           |
| `Procfile`         | commande de démarrage (secours / portable)                  |
| `.python-version`  | version de Python (3.12)                                     |
| `.gitignore`       | **ignore `.env`** → ta clé Gemini ne part PAS sur GitHub     |

Commande de démarrage utilisée :
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```
`$PORT` est injecté automatiquement par Railway — ne le fixe pas toi-même.

---

## Étapes

### 1. Pousser le code sur GitHub
Depuis la racine du projet `AppDePorte/` :
```bash
git init
git add .
git commit -m "AppDePorte"
git branch -M main
git remote add origin https://github.com/<toi>/AppDePorte.git
git push -u origin main
```
> ⚠️ Vérifie que `backend/.env` n'est PAS dans le commit (il est gitignoré).
> `git status` ne doit pas le lister.

### 2. Créer le service sur Railway
1. https://railway.app → **New Project** → **Deploy from GitHub repo** → choisis ton repo.
2. **Important** : comme le backend est dans un sous-dossier, ouvre le service →
   **Settings** → **Root Directory** = `backend`.
   (Railway ne build alors que ce dossier.)

### 3. Configurer les variables d'environnement
Service → **Variables** → ajoute :

| Variable            | Valeur                                  | Obligatoire |
|---------------------|------------------------------------------|-------------|
| `GEMINI_API_KEY`    | ta clé Gemini                            | ✅ oui      |
| `GEMINI_MODEL`      | `gemini-2.5-flash-image`                 | non         |
| `GEMINI_TIMEOUT`    | `120`                                    | non         |
| `FRONTEND_ORIGINS`  | l'URL de ton frontend (voir plus bas)    | recommandé  |

> Ne mets JAMAIS la clé dans le code ou dans un fichier commité.

### 4. Déployer
Railway build et déploie automatiquement. Tu obtiens une URL publique du type :
```
https://appdeporte-production-xxxx.up.railway.app
```
Teste-la :
```
https://....up.railway.app/            -> {"status":"ok",...}
https://....up.railway.app/doors       -> liste des 15 portes
```

À chaque `git push` sur `main`, Railway redéploie tout seul. 🎉

---

## Relier le frontend

Le frontend Next.js appelle le backend via son **proxy interne** `/api`
(voir `frontend/next.config.mjs`, variable `BACKEND_URL`). Sur l'hébergeur du
frontend (Vercel, etc.), définis :

```
BACKEND_URL = https://....up.railway.app
```

Comme les appels passent par le serveur Next (et pas le navigateur), **pas de
souci CORS**. Si un jour tu appelles le backend directement depuis le
navigateur, renseigne alors `FRONTEND_ORIGINS` côté Railway avec l'URL exacte
du frontend.

## Test rapide en local (optionnel)
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate    # (Windows)
pip install -r requirements.txt
set GEMINI_API_KEY=ta_cle                          # PowerShell: $env:GEMINI_API_KEY="ta_cle"
uvicorn main:app --host 0.0.0.0 --port 8000
```
