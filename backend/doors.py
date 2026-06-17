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
        "name": "Rouge bordeaux à panneaux",
        "prompt": (
            "a traditional panelled entry door painted deep bordeaux red, "
            "glossy finish, four moulded panels, polished brass furniture and "
            "a central round knob"
        ),
    },
    {
        "id": "door-5",
        "name": "Bleu pastel campagne",
        "prompt": (
            "a charming country-style entry door painted soft pastel blue, "
            "vertical tongue-and-groove planks, small four-pane window at the "
            "top, wrought iron handle"
        ),
    },
    {
        "id": "door-6",
        "name": "Aluminium noir design",
        "prompt": (
            "a high-end designer aluminium entry door in matte black, smooth "
            "monolithic surface, a single full-height stainless steel vertical "
            "handle, hidden hinges"
        ),
    },
    {
        "id": "door-7",
        "name": "Bois clair scandinave",
        "prompt": (
            "a Scandinavian style entry door in light natural pine, clean flat "
            "surface, one square frosted glass window, minimalist black round "
            "knob"
        ),
    },
    {
        "id": "door-8",
        "name": "Verte forêt cottage",
        "prompt": (
            "a cottage entry door painted forest green, four panels with the "
            "top two glazed with small clear panes, antique bronze handle and "
            "knocker"
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
