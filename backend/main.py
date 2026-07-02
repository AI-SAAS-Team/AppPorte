"""Backend FastAPI — visualisation de portes d'entrée par IA.

Routes :
  GET  /            -> petit health check
  GET  /doors       -> catalogue des 15 modèles de portes
  POST /generate    -> reçoit la photo de l'utilisateur + l'id du modèle,
                       appelle Gemini et renvoie l'image générée (data URL).
"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from doors import DOORS, get_door, get_reference_image
from gemini import GeminiError, detect_door_bbox, generate_door_image

load_dotenv(Path(__file__).parent / ".env")

# Taille max d'upload acceptée (50 Mo).
MAX_UPLOAD_BYTES = 50 * 1024 * 1024
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}

# Origines autorisées pour le frontend (séparées par des virgules dans .env).
_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
ALLOWED_ORIGINS = [o.strip() for o in _origins.split(",") if o.strip()]

app = FastAPI(title="AppDePorte API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def health() -> dict:
    return {"status": "ok", "service": "AppDePorte API"}


@app.get("/doors")
def list_doors() -> dict:
    """Catalogue exposé au frontend (sans le prompt interne)."""
    return {
        "doors": [
            {"id": d["id"], "name": d["name"]}
            for d in DOORS
        ]
    }


def _normalize_image(raw: bytes) -> tuple[bytes, str]:
    """Valide l'image, la convertit en RGB JPEG et la redimensionne si besoin.

    Renvoie (octets, mime). Lève HTTPException 400 si l'image est invalide.
    """
    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Le fichier envoyé n'est pas une image valide.",
        ) from exc

    if image.mode != "RGB":
        image = image.convert("RGB")

    # On borne la dimension max pour limiter le coût et le temps de génération.
    max_side = 1536
    if max(image.size) > max_side:
        image.thumbnail((max_side, max_side), Image.LANCZOS)

    out = io.BytesIO()
    image.save(out, format="JPEG", quality=92)
    return out.getvalue(), "image/jpeg"


def _cover_resize(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Redimensionne en mode "cover" (sans déformer) puis recadre au centre."""
    tw, th = size
    w, h = img.size
    scale = max(tw / w, th / h)
    img = img.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    left = (img.width - tw) // 2
    top = (img.height - th) // 2
    return img.crop((left, top, left + tw, top + th))


def _composite_changed_region(
    original_bytes: bytes, generated_bytes: bytes
) -> tuple[bytes, str]:
    """Ne garde de l'image IA que les zones qui ont changé (la porte).

    Principe : on superpose l'image générée sur l'originale uniquement là où
    les deux diffèrent vraiment. Partout où l'IA a laissé le décor identique,
    on conserve les pixels d'origine -> seule la porte change.

    Dégradation propre : si l'IA a tout redessiné (changement quasi total),
    on renvoie simplement l'image IA recadrée.
    """
    import numpy as np
    from PIL import ImageFilter

    try:
        orig = Image.open(io.BytesIO(original_bytes)).convert("RGB")
        gen = Image.open(io.BytesIO(generated_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        return generated_bytes, "image/png"

    gen = _cover_resize(gen, orig.size)

    a = np.asarray(orig).astype(np.int16)
    b = np.asarray(gen).astype(np.int16)
    # Différence par pixel (canal le plus marqué), 0..255.
    diff = np.abs(a - b).max(axis=2).astype(np.uint8)

    # Seuil : en dessous, on considère le décor "inchangé" -> on garde l'original.
    threshold = 28
    raw_mask = (diff > threshold).astype(np.uint8) * 255

    changed_ratio = float((raw_mask > 0).mean())
    # Si presque toute l'image a changé, le compositing n'a pas de sens.
    if changed_ratio > 0.85:
        out = io.BytesIO()
        gen.save(out, format="PNG")
        return out.getvalue(), "image/png"

    mask = Image.fromarray(raw_mask, "L")
    # Nettoyage morphologique : on retire les petits points (érosion) puis on
    # regrossit pour bien couvrir la porte (dilatation), enfin on adoucit.
    mask = mask.filter(ImageFilter.MinFilter(3))
    mask = mask.filter(ImageFilter.MaxFilter(9))
    mask = mask.filter(ImageFilter.GaussianBlur(5))

    result = Image.composite(gen, orig, mask)
    out = io.BytesIO()
    result.save(out, format="PNG")
    return out.getvalue(), "image/png"


def _remove_light_background(ref: Image.Image) -> Image.Image:
    """Supprime le fond clair/blanc d'une image de porte via flood fill depuis les bords.

    Contrairement à un seuillage global, le flood fill ne supprime que les pixels
    connectés aux bords ET proches de la couleur de fond — la porte elle-même
    (même grise ou claire) reste intacte car elle n'est pas connectée au fond.
    """
    import numpy as np
    from collections import deque

    ref = ref.convert("RGBA")
    arr = np.array(ref)

    # Si transparence existante significative, on l'utilise directement
    if arr[:, :, 3].min() < 200:
        return ref

    h, w = arr.shape[:2]

    # Couleur de fond estimée depuis les coins
    patch = max(3, min(8, h // 30, w // 30))
    corners = [
        arr[:patch, :patch, :3],
        arr[:patch, w - patch:, :3],
        arr[h - patch:, :patch, :3],
        arr[h - patch:, w - patch:, :3],
    ]
    bg_color = (
        np.concatenate([c.reshape(-1, 3) for c in corners], axis=0)
        .mean(axis=0)
        .astype(np.float32)
    )

    diff = np.abs(arr[:, :, :3].astype(np.float32) - bg_color).max(axis=2)
    tolerance = 45

    # BFS depuis tous les pixels de bordure proches du fond
    bg_mask = np.zeros((h, w), dtype=bool)
    queue: deque = deque()

    for x in range(w):
        for y in (0, h - 1):
            if diff[y, x] < tolerance and not bg_mask[y, x]:
                bg_mask[y, x] = True
                queue.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if diff[y, x] < tolerance and not bg_mask[y, x]:
                bg_mask[y, x] = True
                queue.append((y, x))

    while queue:
        y, x = queue.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not bg_mask[ny, nx] and diff[ny, nx] < tolerance:
                bg_mask[ny, nx] = True
                queue.append((ny, nx))

    arr[:, :, 3] = np.where(bg_mask, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def _composite_reference_door(
    original_bytes: bytes,
    reference_path: Path,
    bbox: dict[str, int],
) -> tuple[bytes, str]:
    """Colle directement l'image de référence sur la photo originale.

    Les pixels de fond (transparents après suppression du fond blanc) sont
    remplacés par la couleur du mur prélevée autour de la porte — l'ancienne
    porte ne transparaît plus du tout. On colle ensuite le patch en dur dans
    la zone détectée, avec un léger fondu sur les 4 bords pour la jonction.
    """
    import numpy as np

    orig = Image.open(io.BytesIO(original_bytes)).convert("RGB")
    ref = Image.open(reference_path)

    x1 = max(0, min(bbox["x1"], orig.width - 2))
    y1 = max(0, min(bbox["y1"], orig.height - 2))
    x2 = max(x1 + 2, min(bbox["x2"], orig.width))
    y2 = max(y1 + 2, min(bbox["y2"], orig.height))
    door_w, door_h = x2 - x1, y2 - y1

    ref_clean = _remove_light_background(ref)
    ref_resized = ref_clean.resize((door_w, door_h), Image.LANCZOS)

    ref_arr = np.array(ref_resized)
    alpha = ref_arr[:, :, 3]
    door_rgb = ref_arr[:, :, :3].astype(np.float32)

    orig_arr = np.array(orig)

    # Couleur du mur : prélevée dans une bordure de 20px autour de la porte
    margin = 20
    patches = []
    if y1 >= margin:
        patches.append(orig_arr[y1 - margin:y1, x1:x2].reshape(-1, 3))
    if y2 + margin <= orig.height:
        patches.append(orig_arr[y2:y2 + margin, x1:x2].reshape(-1, 3))
    if x1 >= margin:
        patches.append(orig_arr[y1:y2, x1 - margin:x1].reshape(-1, 3))
    if x2 + margin <= orig.width:
        patches.append(orig_arr[y1:y2, x2:x2 + margin].reshape(-1, 3))
    wall_color = (
        np.concatenate(patches, axis=0).mean(axis=0).astype(np.float32)
        if patches else np.array([180.0, 180.0, 180.0])
    )

    # Pixels de fond → couleur du mur (pas l'ancienne porte)
    is_bg = alpha < 128
    door_rgb[is_bg] = wall_color

    # Correction de luminosité sur les pixels de la porte elle-même
    scene_mean = float(orig_arr[y1:y2, x1:x2].mean())
    visible = ~is_bg
    if visible.any():
        ref_mean = float(door_rgb[visible].mean())
        if ref_mean > 5:
            factor = min(max(scene_mean / ref_mean, 0.4), 2.2)
            door_rgb[visible] = np.clip(door_rgb[visible] * factor, 0, 255)

    patch = door_rgb.astype(np.uint8)

    # Fondu doux sur les bords du bbox (5 px) pour une jonction propre
    feather = 5
    blend_mask = np.ones((door_h, door_w), dtype=np.float32)
    for i in range(feather):
        s = (i + 1) / feather
        blend_mask[i, :] = np.minimum(blend_mask[i, :], s)
        blend_mask[door_h - 1 - i, :] = np.minimum(blend_mask[door_h - 1 - i, :], s)
        blend_mask[:, i] = np.minimum(blend_mask[:, i], s)
        blend_mask[:, door_w - 1 - i] = np.minimum(blend_mask[:, door_w - 1 - i], s)

    orig_patch = orig_arr[y1:y2, x1:x2].astype(np.float32)
    blended = (
        patch.astype(np.float32) * blend_mask[:, :, np.newaxis]
        + orig_patch * (1 - blend_mask[:, :, np.newaxis])
    ).astype(np.uint8)

    result = orig.copy()
    result.paste(Image.fromarray(blended), (x1, y1))

    out = io.BytesIO()
    result.save(out, format="PNG")
    return out.getvalue(), "image/png"


@app.post("/generate")
async def generate(
    file: UploadFile = File(...),
    door_id: str = Form(...),
) -> JSONResponse:
    door = get_door(door_id)
    if door is None:
        raise HTTPException(status_code=400, detail="Modèle de porte inconnu.")

    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilisez une image JPEG, PNG ou WebP.",
        )

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Fichier vide.")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Image trop lourde (max 50 Mo).",
        )

    user_image, user_mime = _normalize_image(raw)

    ref_path = get_reference_image(door_id)

    # Étape 1 : détection de la porte + compositing direct de l'image de référence.
    # C'est la voie prioritaire : elle reproduit la porte du catalogue à l'identique.
    if ref_path is not None:
        try:
            orig_img = Image.open(io.BytesIO(user_image))
            img_w, img_h = orig_img.size
            bbox = await detect_door_bbox(user_image, user_mime, img_w, img_h)
            if bbox is not None:
                image_bytes, mime = _composite_reference_door(user_image, ref_path, bbox)
                data_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"
                return JSONResponse({"image": data_url, "door": {"id": door["id"], "name": door["name"]}})
        except Exception:
            pass  # Échec silencieux → on continue vers Gemini

    # Étape 2 (fallback) : génération par Gemini si la détection a échoué
    # ou si aucune image de référence n'existe pour ce modèle.
    try:
        image_bytes, mime = await generate_door_image(
            user_image=user_image,
            user_image_mime=user_mime,
            door_name=door["name"],
            door_prompt=door["prompt"],
            reference_image=ref_path,
        )
    except GeminiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    image_bytes, mime = _composite_changed_region(user_image, image_bytes)

    data_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"
    return JSONResponse(
        {
            "image": data_url,
            "door": {"id": door["id"], "name": door["name"]},
        }
    )
