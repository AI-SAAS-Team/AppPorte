"""Catalogue des 15 modèles de portes proposés sur le site.

Chaque modèle a :
- id        : identifiant unique utilisé par le frontend (door-1 ... door-15)
- name      : nom affiché
- image     : nom du fichier d'aperçu dans le dossier `assets/`
- prompt    : description détaillée envoyée à l'IA pour décrire la porte cible

L'image d'aperçu (`assets/door-X.*`) est ENVOYÉE à Gemini comme image de
référence lorsqu'elle existe : remplacez les placeholders par de vraies photos
de portes pour de meilleurs résultats. La description texte (`prompt`) sert de
secours / de précision même quand l'image de référence est un placeholder.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

ASSETS_DIR = Path(__file__).parent / "assets"

DOORS = [
    {
        "id": "door-1",
        "name": "Anthracite vitrage latéral",
        "prompt": (
            "a modern anthracite grey (RAL 7016) aluminium entry door with a "
            "smooth matte finish and subtle horizontal grooved lines, a tall "
            "narrow vertical frosted glass strip on the right side, a brushed "
            "stainless steel lever handle on the left"
        ),
    },
    {
        "id": "door-2",
        "name": "Anthracite à rainures",
        "prompt": (
            "a modern anthracite grey (RAL 7016) entry door with full-width "
            "horizontal grooved slats across the surface, smooth matte finish, "
            "a brushed steel lever handle on the left, and a discreet "
            "ventilation grille at the bottom"
        ),
    },
    {
        "id": "door-3",
        "name": "Blanche lignes horizontales",
        "prompt": (
            "a clean modern white entry door with a framed raised panel and "
            "four thin horizontal brushed-metal and frosted glass inlay "
            "strips, smooth finish, a satin steel lever handle on the right"
        ),
    },
    {
        "id": "door-4",
        "name": "Anthracite vitrage diagonal",
        "prompt": (
            "a modern anthracite grey (RAL 7016) aluminium entry door, smooth "
            "matte finish, with a large dramatic diagonal/triangular frosted "
            "glass panel crossed by horizontal stainless steel strips on the "
            "left side, and a long vertical brushed steel bar handle on the right"
        ),
    },
    {
        "id": "door-5",
        "name": "Double porte anthracite",
        "prompt": (
            "a modern double-leaf (two equal panels) anthracite grey entry "
            "door, smooth matte finish, with horizontal stainless steel inlay "
            "strips across both leaves, and two long vertical brushed steel bar "
            "handles meeting at the centre"
        ),
    },
    {
        "id": "door-6",
        "name": "Chêne clair vitrage vertical",
        "prompt": (
            "a contemporary light oak wood entry door with horizontal wood "
            "planks, a tall narrow vertical frosted glass strip on the right, "
            "and a rectangular brushed stainless steel letter-plate on the left"
        ),
    },
    {
        "id": "door-7",
        "name": "Anthracite vitrage horizontal",
        "prompt": (
            "a modern anthracite grey entry door, smooth matte finish, with "
            "frosted glass panes divided by horizontal stainless steel strips "
            "on the left half, and a long vertical brushed steel bar handle on "
            "the right"
        ),
    },
    {
        "id": "door-8",
        "name": "Noyer foncé vitré inox",
        "prompt": (
            "a modern dark walnut (wenge) wood entry door with a brushed "
            "stainless steel kickplate at the bottom, a central frosted glass "
            "panel crossed by four horizontal steel strips, and a lever handle "
            "plus a long vertical bar handle on the left"
        ),
    },
    {
        "id": "door-9",
        "name": "Blanche moderne lisse",
        "prompt": (
            "a clean modern entry door in smooth pure white, completely flat "
            "flush surface, a long brushed nickel vertical bar handle, "
            "contemporary look"
        ),
    },
    {
        "id": "door-10",
        "name": "Acier industriel verrière",
        "prompt": (
            "an industrial style steel entry door, black metal frame divided "
            "into a grid of clear glass panes like a factory window, riveted "
            "details, matte black tubular handle"
        ),
    },
    {
        "id": "door-11",
        "name": "Noyer foncé à rainures",
        "prompt": (
            "an elegant entry door in dark walnut wood, horizontal grooved "
            "slats running across the full width, recessed stainless steel "
            "handle, warm rich tone"
        ),
    },
    {
        "id": "door-12",
        "name": "Art déco vitrail",
        "prompt": (
            "an Art Deco entry door in cream lacquer, geometric stained glass "
            "panel with amber and teal accents, polished brass fan-shaped "
            "details and handle"
        ),
    },
    {
        "id": "door-13",
        "name": "Gris béton mat",
        "prompt": (
            "a contemporary entry door with a smooth concrete-grey matte "
            "finish, a single narrow vertical slot of frosted glass, minimal "
            "black recessed handle"
        ),
    },
    {
        "id": "door-14",
        "name": "Bois & verre demi-lune",
        "prompt": (
            "a warm medium-brown wooden entry door with a large semicircular "
            "fanlight of clear glass at the top, two vertical panels below, "
            "antique brass handle"
        ),
    },
    {
        "id": "door-15",
        "name": "Jaune moutarde rétro",
        "prompt": (
            "a retro mid-century entry door painted mustard yellow, three small "
            "round porthole windows arranged diagonally, satin chrome handle"
        ),
    },
]

_BY_ID = {d["id"]: d for d in DOORS}

_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".svg")


def get_door(door_id: str) -> Optional[dict]:
    """Retourne le dict du modèle pour un id donné, ou None s'il n'existe pas."""
    return _BY_ID.get(door_id)


def get_reference_image(door_id: str) -> Optional[Path]:
    """Retourne le chemin de l'image de référence si un fichier raster existe.

    Les SVG (placeholders) ne sont pas envoyés à Gemini car le modèle attend du
    raster (jpg/png/webp). On se rabat alors sur la description texte seule.
    """
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        candidate = ASSETS_DIR / f"{door_id}{ext}"
        if candidate.exists():
            return candidate
    return None
