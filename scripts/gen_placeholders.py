"""Génère 15 aperçus SVG de portes (placeholders) dans frontend/public/doors/.

Remplacez ces SVG par de vraies photos (door-1.jpg ... door-15.jpg) quand
vous les avez : mettez-les dans frontend/public/doors/ pour l'aperçu et dans
backend/assets/ pour servir de référence visuelle à l'IA.

    py scripts/gen_placeholders.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "frontend" / "public" / "doors"
OUT.mkdir(parents=True, exist_ok=True)

# (nom, couleur porte, couleur panneau/accent, couleur poignée)
DOORS = [
    ("Contemporaine anthracite", "#3a3f44", "#2b2f33", "#c9ccd1"),
    ("Classique bois chêne", "#9c6b3f", "#7d5530", "#d8b572"),
    ("Vitrée minimaliste", "#cfd8dc", "#9fb3bd", "#1c1c1c"),
    ("Rouge bordeaux", "#6e1423", "#56101c", "#d4af37"),
    ("Bleu pastel campagne", "#9bc1d4", "#7fa9bd", "#444"),
    ("Aluminium noir", "#1b1b1b", "#111111", "#b8c0c6"),
    ("Bois clair scandinave", "#d9bd95", "#c4a679", "#222"),
    ("Verte forêt cottage", "#274d36", "#1d3b2a", "#b5894f"),
    ("Blanche moderne", "#f2f2ef", "#e0e0db", "#9aa0a6"),
    ("Acier industriel", "#2c2c2c", "#1a1a1a", "#8a8f94"),
    ("Noyer foncé rainures", "#4a3325", "#382518", "#c0c4c8"),
    ("Art déco vitrail", "#efe7d6", "#d9b04a", "#b8860b"),
    ("Gris béton mat", "#8c8f91", "#76797b", "#2b2b2b"),
    ("Bois & verre demi-lune", "#8a5a34", "#6e4527", "#d4af37"),
    ("Jaune moutarde rétro", "#d9a520", "#bd8c12", "#cfd3d6"),
]


def make_svg(idx: int, name: str, door: str, panel: str, handle: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="560" viewBox="0 0 400 560">
  <rect width="400" height="560" fill="#e8e4dc"/>
  <rect x="60" y="40" width="280" height="480" rx="6" fill="{door}" stroke="#00000022" stroke-width="2"/>
  <rect x="90" y="80" width="100" height="190" rx="4" fill="{panel}"/>
  <rect x="210" y="80" width="100" height="190" rx="4" fill="{panel}"/>
  <rect x="90" y="300" width="100" height="170" rx="4" fill="{panel}"/>
  <rect x="210" y="300" width="100" height="170" rx="4" fill="{panel}"/>
  <rect x="300" y="270" width="14" height="60" rx="7" fill="{handle}"/>
  <rect x="0" y="520" width="400" height="40" fill="#cfc9bd"/>
  <text x="200" y="546" font-family="Segoe UI, Arial, sans-serif" font-size="18"
        font-weight="600" fill="#3a342b" text-anchor="middle">{idx}. {name}</text>
</svg>
"""


for i, (name, door, panel, handle) in enumerate(DOORS, start=1):
    svg = make_svg(i, name, door, panel, handle)
    (OUT / f"door-{i}.svg").write_text(svg, encoding="utf-8")

print(f"{len(DOORS)} aperçus SVG écrits dans {OUT}")
