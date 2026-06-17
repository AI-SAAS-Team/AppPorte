# Déployer le frontend sur Firebase Hosting

Le frontend est exporté en **statique** (`output: export`) et appelle
directement le backend Railway. Hébergement gratuit, pas de plan Blaze requis.

## Prérequis (une seule fois)
1. Crée un projet sur https://console.firebase.google.com (note son **Project ID**).
2. Installe le CLI et connecte-toi :
   ```bash
   npm install -g firebase-tools
   firebase login
   ```
3. Renseigne ton Project ID dans `frontend/.firebaserc`
   (remplace `REMPLACE_PAR_TON_PROJECT_ID`), ou lance `firebase use --add`.

## Déployer
Depuis le dossier `frontend/` :
```bash
npm install
npm run build:firebase     # genere le dossier out/ (URL Railway gravee)
firebase deploy --only hosting
```
Firebase te donne l'URL : `https://TON_PROJECT.web.app`

À chaque mise à jour : refais `npm run build:firebase` puis `firebase deploy`.

## ⚠️ ÉTAPE CRITIQUE : autoriser le CORS côté Railway
Comme le navigateur appelle l'API Railway **directement**, le backend doit
autoriser le domaine Firebase. Sur Railway → service backend → **Variables** :

```
FRONTEND_ORIGINS = https://TON_PROJECT.web.app,https://TON_PROJECT.firebaseapp.com
```

(Railway redéploie tout seul.) Sans ça, la génération échouera avec une erreur
CORS dans le navigateur.

> Astuce : pour tester vite, tu peux mettre `FRONTEND_ORIGINS = *` (l'app
> n'utilise pas de cookies), puis resserrer ensuite sur tes domaines.

## L'URL du backend change ?
Elle est gravée dans le build via le script `build:firebase`
(`NEXT_PUBLIC_API_URL=https://appporte-production.up.railway.app`).
Si ton URL Railway change, modifie ce script dans `package.json` puis rebuild.
