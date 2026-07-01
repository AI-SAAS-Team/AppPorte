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
        "name": "Gris vitrage dépoli lignes",
        "prompt": (
            "a modern grey aluminium entry door with a smooth matte finish, "
            "a large full-height frosted glass panel covering most of the door "
            "surface, with delicate vertical etched lines decorating the glass, "
            "and a long vertical brushed stainless steel bar handle on the left"
        ),
    },
    {
        "id": "door-2",
        "name": "Double porte noire diagonale",
        "prompt": (
            "a modern double-leaf entry door with a dark grey aluminium frame, "
            "both leaves finished in matte black with a bold diagonal triangular "
            "design element, multiple horizontal stainless steel inlay strips "
            "across both panels, and two lever handles with a digital lock in "
            "the centre"
        ),
    },
    {
        "id": "door-3",
        "name": "Noire bandes vitrées",
        "prompt": (
            "a contemporary matte black entry door with a smooth finish, "
            "featuring multiple narrow horizontal frosted glass strips evenly "
            "spaced across the full width of the door, a narrow vertical frosted "
            "glass strip on the left side, and a brushed steel lever handle on "
            "the left"
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
        "name": "Aluminium gris & beige",
        "prompt": (
            "a modern aluminium entry door with a brushed silver-grey frame and "
            "a two-tone face: on the left a vertical frosted glass strip crossed "
            "by horizontal stainless steel bars, on the right a large cream/beige "
            "panel divided by thin horizontal grooves, with a distinctive curved "
            "brushed steel lever handle in the centre"
        ),
    },
    {
        "id": "door-10",
        "name": "Anthracite impostes vitrées",
        "prompt": (
            "a modern anthracite grey aluminium entry door flanked by two "
            "frosted glass sidelights, the central leaf crossed by horizontal "
            "stainless steel strips, with a long vertical brushed steel bar "
            "handle"
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
