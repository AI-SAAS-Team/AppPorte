"""Importe de vraies photos de portes dans l'app.

Déposez vos images dans `AppDePorte/incoming/` puis lancez :

    py scripts/import_doors.py

Le script associe les fichiers (tri alphabétique) aux modèles door-1, door-2,
door-3, ... Pour chaque image il :
  - crée un aperçu pour la galerie  -> frontend/public/doors/door-N.jpg
  - crée une référence pour l'IA      -> backend/assets/door-N.jpg

Vous pouvez forcer l'ordre en nommant vos fichiers 1.png, 2.png, 3.png (ou
door-1.*, door-2.*...). Tout format courant est accepté (png/jpg/jpeg/webp).
"""

from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INCOMING = ROOT / "incoming"
GALLERY = ROOT / "frontend" / "public" / "doors"
ASSETS = ROOT / "backend" / "assets"

EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def main() -> int:
    if not INCOMING.exists():
        INCOMING.mkdir(parents=True)
        print(f"Dossier créé : {INCOMING}\nDéposez-y vos images puis relancez.")
        return 0

    files = sorted(
        [p for p in INCOMING.iterdir() if p.suffix.lower() in EXTS],
        key=lambda p: p.name.lower(),
    )
    if not files:
        print(f"Aucune image trouvée dans {INCOMING}. Déposez-y vos photos.")
        return 1

    GALLERY.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    for i, src in enumerate(files, start=1):
        door_id = f"door-{i}"
        img = Image.open(src)
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Référence IA : qualité conservée, bornée à 1536 px.
        ref = img.copy()
        if max(ref.size) > 1536:
            ref.thumbnail((1536, 1536), Image.LANCZOS)
        ref.save(ASSETS / f"{door_id}.jpg", "JPEG", quality=92)

        # Aperçu galerie : plus léger.
        prev = img.copy()
        prev.thumbnail((800, 800), Image.LANCZOS)
        prev.save(GALLERY / f"{door_id}.jpg", "JPEG", quality=85)

        # Supprime l'ancien placeholder SVG s'il existe.
        old_svg = GALLERY / f"{door_id}.svg"
        if old_svg.exists():
            old_svg.unlink()

        print(f"{src.name}  ->  {door_id} (galerie + assets IA)")

    print(
        f"\n{len(files)} porte(s) importée(s). "
        "Pensez à mettre à jour les noms/descriptions dans "
        "backend/doors.py et frontend/lib/doors.ts si besoin."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
