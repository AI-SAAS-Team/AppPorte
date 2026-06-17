"""Recrée des rendus fidèles des 3 portes fournies par l'utilisateur.

Produit des fichiers JPG (sur fond blanc, façon photo studio) pour :
  - door-1 : anthracite, vitrage vertical à droite, poignée gauche
  - door-2 : anthracite, rainures horizontales pleine largeur, poignée droite,
             grille d'aération en bas
  - door-3 : blanche, panneau encadré, 4 fines bandes horizontales, poignée droite

Sortie -> frontend/public/doors/door-N.jpg  et  backend/assets/door-N.jpg
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
GALLERY = ROOT / "frontend" / "public" / "doors"
ASSETS = ROOT / "backend" / "assets"
GALLERY.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)

W, H = 640, 900

ANTH = (58, 63, 71)
ANTH_DARK = (44, 48, 55)
ANTH_LINE = (78, 84, 92)
GLASS = (226, 234, 236)
STEEL = (176, 182, 188)
STEEL_DARK = (120, 126, 132)
WHITE_DOOR = (244, 245, 246)
WHITE_FRAME = (250, 250, 250)
GREY_LINE = (150, 156, 162)
SHADOW = (210, 210, 210)


def base(bg=(255, 255, 255)):
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)


def frame_and_leaf(d, leaf_color, frame_color, frame_outline):
    # cadre extérieur
    d.rectangle([70, 46, 570, 852], fill=frame_color, outline=frame_outline, width=2)
    # ombre légère du vantail
    d.rectangle([96, 70, 548, 832], fill=SHADOW)
    # vantail
    d.rectangle([92, 66, 544, 828], fill=leaf_color)
    return (92, 66, 544, 828)  # bbox du vantail


def lever_handle(d, cx, mid_y, point_left=True):
    """Poignée bec-de-cane + serrure ronde."""
    # rosace
    d.rounded_rectangle([cx - 9, mid_y - 26, cx + 9, mid_y + 26], radius=9, fill=STEEL)
    if point_left:
        d.rounded_rectangle([cx - 62, mid_y - 5, cx + 4, mid_y + 5], radius=5, fill=STEEL)
        d.ellipse([cx - 70, mid_y - 7, cx - 56, mid_y + 7], fill=STEEL)
    else:
        d.rounded_rectangle([cx - 4, mid_y - 5, cx + 62, mid_y + 5], radius=5, fill=STEEL)
        d.ellipse([cx + 56, mid_y - 7, cx + 70, mid_y + 7], fill=STEEL)
    # cylindre de serrure
    d.ellipse([cx - 7, mid_y + 44, cx + 7, mid_y + 58], fill=STEEL_DARK)
    d.rectangle([cx - 3, mid_y + 52, cx + 3, mid_y + 60], fill=STEEL_DARK)


def make_door1():
    img, d = base()
    x0, y0, x1, y1 = frame_and_leaf(d, ANTH, ANTH, ANTH_DARK)
    # rainures horizontales subtiles (pas pleine largeur, façon image 1)
    for y in (235, 285, 470, 520, 715, 765):
        d.line([(x0 + 26, y), (x1 - 26, y)], fill=ANTH_LINE, width=2)
    # vitrage vertical à droite du centre
    gx0, gy0, gx1, gy1 = 392, 150, 452, 745
    d.rectangle([gx0 - 2, gy0 - 2, gx1 + 2, gy1 + 2], fill=ANTH_DARK)
    d.rectangle([gx0, gy0, gx1, gy1], fill=GLASS)
    # poignée à gauche
    lever_handle(d, 214, 492, point_left=True)
    return img


def make_door2():
    img, d = base()
    x0, y0, x1, y1 = frame_and_leaf(d, ANTH, ANTH, ANTH_DARK)
    # rainures horizontales pleine largeur
    for y in range(150, 720, 95):
        d.line([(x0 + 18, y), (x1 - 18, y)], fill=ANTH_LINE, width=2)
    # poignée à droite
    lever_handle(d, 470, 470, point_left=True)
    # grille d'aération en bas
    gy = 770
    for i in range(5):
        yy = gy + i * 9
        d.line([(x0 + 120, yy), (x1 - 120, yy)], fill=ANTH_LINE, width=3)
    return img


def make_door3():
    img, d = base((238, 239, 240))
    # cadre + vantail blancs
    d.rectangle([70, 46, 570, 852], fill=WHITE_FRAME, outline=(205, 207, 210), width=2)
    d.rectangle([96, 70, 548, 832], fill=(225, 226, 228))
    d.rectangle([92, 66, 544, 828], fill=WHITE_DOOR)
    # panneau encadré
    d.rectangle([126, 104, 510, 792], outline=(206, 208, 211), width=3)
    # 4 fines bandes horizontales (métal/verre dépoli)
    for y in (215, 360, 505, 650):
        d.line([(150, y), (486, y)], fill=GREY_LINE, width=4)
        d.line([(150, y + 3), (486, y + 3)], fill=(200, 204, 208), width=1)
    # poignée à droite
    lever_handle(d, 474, 470, point_left=True)
    # seuil bas
    d.rectangle([96, 818, 548, 832], fill=(200, 202, 205))
    return img


def save(img, door_id):
    ref = img.copy()
    ref.save(ASSETS / f"{door_id}.jpg", "JPEG", quality=92)
    prev = img.copy()
    prev.thumbnail((800, 800), Image.LANCZOS)
    prev.save(GALLERY / f"{door_id}.jpg", "JPEG", quality=88)
    old = GALLERY / f"{door_id}.svg"
    if old.exists():
        old.unlink()
    print(f"{door_id}.jpg écrit (galerie + assets)")


save(make_door1(), "door-1")
save(make_door2(), "door-2")
save(make_door3(), "door-3")
print("Terminé.")
