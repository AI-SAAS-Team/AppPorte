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

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from doors import DOORS, get_door, get_reference_image
from gemini import GeminiError, generate_door_image

load_dotenv()

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

    try:
        image_bytes, mime = await generate_door_image(
            user_image=user_image,
            user_image_mime=user_mime,
            door_name=door["name"],
            door_prompt=door["prompt"],
            reference_image=get_reference_image(door_id),
        )
    except GeminiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    # On ne garde de l'image IA que la zone réellement modifiée (la porte) et
    # on conserve le reste de la photo d'origine au pixel près.
    image_bytes, mime = _composite_changed_region(user_image, image_bytes)

    data_url = f"data:{mime};base64,{base64.b64encode(image_bytes).decode('ascii')}"
    return JSONResponse(
        {
            "image": data_url,
            "door": {"id": door["id"], "name": door["name"]},
        }
    )
