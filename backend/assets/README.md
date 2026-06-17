# Images de référence des portes (côté IA)

Déposez ici de **vraies photos** des 15 modèles de portes, nommées :

```
door-1.jpg   door-2.jpg   ...   door-15.jpg
```

(les extensions `.jpg`, `.jpeg`, `.png`, `.webp` sont acceptées)

Quand un fichier `door-X.{jpg,png,webp}` est présent, il est envoyé à Gemini
comme **image de référence** du modèle choisi, ce qui améliore nettement le
réalisme du résultat. En l'absence de fichier, seule la description texte du
modèle (voir `backend/doors.py`) est utilisée.

Les aperçus affichés dans la galerie du site sont, eux, dans
`frontend/public/doors/` (placeholders SVG par défaut).
