# AppDePorte 🚪

Application web de **visualisation de portes d'entrée par IA**.
L'utilisateur photographie sa porte, choisit l'un des 15 modèles proposés, et
l'IA (Gemini) génère un rendu photoréaliste où seule la porte est remplacée —
façade, cadrage, lumière et perspective d'origine conservés.

## Stack

- **Frontend** : Next.js 15 (App Router, TypeScript, Tailwind CSS v4)
- **Backend** : FastAPI (Python)
- **IA image** : API Gemini (`gemini-2.5-flash-image`)

## Structure

```
AppDePorte/
├── backend/              # API FastAPI
│   ├── main.py           # routes (/doors, /generate)
│   ├── gemini.py         # client API Gemini
│   ├── doors.py          # catalogue des 15 modèles + descriptions
│   ├── assets/           # (optionnel) vraies photos de référence door-1.jpg…
│   ├── requirements.txt
│   ├── .env              # VOS secrets (non commité)
│   └── .env.example
├── frontend/             # App Next.js
│   ├── app/              # page d'accueil + layout
│   ├── components/       # PhotoCapture, DoorGallery, ResultView
│   ├── lib/doors.ts      # catalogue côté client
│   ├── public/doors/     # aperçus des 15 portes (SVG placeholders)
│   ├── .env.local        # NEXT_PUBLIC_API_URL
│   └── .env.example
└── scripts/gen_placeholders.py   # (re)génère les aperçus SVG
```

## Prérequis

- Python 3.10+
- Node.js 18+ et npm
- Une clé API Gemini : https://aistudio.google.com/apikey

---

## 1. Backend (FastAPI)

```bash
cd backend

# Créer et activer un environnement virtuel
python -m venv .venv
# Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# macOS / Linux :
# source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer la clé API
cp .env.example .env      # (Windows : copy .env.example .env)
# puis éditez .env et renseignez GEMINI_API_KEY

# Lancer l'API (port 8000)
uvicorn main:app --reload --port 8000
```

API dispo sur http://localhost:8000 — docs interactives : http://localhost:8000/docs

> **Sécurité** : la clé vit uniquement dans `backend/.env`, qui est dans le
> `.gitignore`. Ne la commitez jamais. Si une clé a fuité, régénérez-la.

## 2. Frontend (Next.js)

Dans un **second terminal** :

```bash
cd frontend

# Installer les dépendances
npm install

# Configurer l'URL du backend (déjà fait par défaut)
cp .env.example .env.local   # (Windows : copy .env.example .env.local)
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Lancer le serveur de dev (port 3000)
npm run dev
```

Ouvrez http://localhost:3000.

---

## Utilisation

1. **Ajoutez une photo** de votre porte (fichier ou caméra sur mobile).
2. **Choisissez un modèle** dans la galerie (15 portes).
3. Cliquez sur **« Générer ma porte »**.
4. Comparez **avant / après** avec le curseur, puis **téléchargez** le rendu.

## Personnaliser les modèles de portes

- **Aperçus de la galerie** : remplacez les SVG dans `frontend/public/doors/`
  (ou régénérez-les via `py scripts/gen_placeholders.py`). Vous pouvez aussi
  déposer des `door-1.jpg … door-15.jpg` et adapter les chemins dans
  `frontend/lib/doors.ts`.
- **Référence IA** : déposez de vraies photos `door-1.jpg … door-15.jpg` dans
  `backend/assets/` — elles seront envoyées à l'IA comme modèle visuel (voir
  `backend/assets/README.md`). Sinon, seule la description texte de chaque porte
  (dans `backend/doors.py`) est utilisée.

## Gestion des erreurs

Le backend renvoie des messages clairs (HTTP 4xx/5xx) pour : fichier vide ou non
image, format non supporté, image trop lourde (>50 Mo), clé API manquante,
timeout de l'IA, blocage de sécurité, ou échec réseau. Le frontend les affiche
en l'état, y compris « backend injoignable ».

## Variables d'environnement

| Côté     | Variable               | Rôle                                   |
|----------|------------------------|----------------------------------------|
| Backend  | `GEMINI_API_KEY`       | **(obligatoire)** clé API Gemini       |
| Backend  | `GEMINI_MODEL`         | modèle d'image (défaut nano-banana)    |
| Backend  | `GEMINI_TIMEOUT`       | timeout en secondes (défaut 120)       |
| Backend  | `FRONTEND_ORIGINS`     | origines CORS autorisées               |
| Frontend | `NEXT_PUBLIC_API_URL`  | URL du backend (défaut localhost:8000) |
