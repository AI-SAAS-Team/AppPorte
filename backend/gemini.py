"""Petit client pour l'API Gemini (génération / édition d'image).

On utilise le modèle d'image de Google (« Nano Banana »,
`gemini-2.5-flash-image`) via l'endpoint REST `generateContent`.

On envoie au modèle :
  1. la photo de la porte d'origine de l'utilisateur (image inline),
  2. éventuellement une photo de référence du modèle de porte choisi,
  3. un prompt texte décrivant précisément le remplacement à effectuer.

Le modèle renvoie une image inline (base64) que l'on relit côté backend.
"""

from __future__ import annotations

import base64
import json as _json
import os
import re as _re
from pathlib import Path
from typing import Optional

import httpx

# Modèle d'édition/génération d'image de Gemini.
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-image")
API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Délai max pour l'appel à l'API (la génération d'image peut être lente).
REQUEST_TIMEOUT = float(os.getenv("GEMINI_TIMEOUT", "120"))


class GeminiError(Exception):
    """Erreur métier renvoyée au frontend avec un message clair."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def build_prompt(door_name: str, door_prompt: str) -> str:
    return (
        "You are a photo editing expert. I will give you two images:\n"
        "- Image 1: a real photo of a house or building with a front door.\n"
        "- Image 2: a product photo of a new door on a white background.\n\n"
        "Your task: swap the existing front door in Image 1 with the door from Image 2.\n\n"
        "Rules:\n"
        "1. The new door must look exactly like the door in Image 2 "
        "(same design, color, materials, hardware).\n"
        "2. Fit the new door into the exact same position, size and perspective "
        "as the original door — do not move or resize the door opening.\n"
        "3. Adapt the new door's lighting and shadows to match the scene in Image 1 "
        "so the result looks photorealistic.\n"
        "4. Do not change anything else: walls, windows, ground, plants, sky, "
        "door frame — everything outside the door leaf stays pixel-perfect identical.\n\n"
        "Output only the edited version of Image 1."
    )


def _file_to_part(path: Path) -> dict:
    mime = "image/png"
    suffix = path.suffix.lower()
    if suffix in (".jpg", ".jpeg"):
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"inline_data": {"mime_type": mime, "data": data}}


def _bytes_to_part(data: bytes, mime_type: str) -> dict:
    encoded = base64.b64encode(data).decode("ascii")
    return {"inline_data": {"mime_type": mime_type, "data": encoded}}


async def generate_door_image(
    *,
    user_image: bytes,
    user_image_mime: str,
    door_name: str,
    door_prompt: str,
    reference_image: Optional[Path] = None,
) -> tuple[bytes, str]:
    """Appelle Gemini et renvoie (octets de l'image générée, mime type).

    Lève GeminiError avec un message lisible en cas de problème.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise GeminiError(
            "La clé GEMINI_API_KEY n'est pas configurée côté serveur.",
            status_code=500,
        )

    parts: list[dict] = [
        {"text": build_prompt(door_name, door_prompt)},
        _bytes_to_part(user_image, user_image_mime),
    ]
    if reference_image is not None:
        parts.append(_file_to_part(reference_image))

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }

    url = f"{API_BASE}/models/{MODEL}:generateContent"
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=headers)
    except httpx.TimeoutException as exc:
        raise GeminiError(
            "L'IA met trop de temps à répondre (timeout). Réessayez.",
            status_code=504,
        ) from exc
    except httpx.HTTPError as exc:
        raise GeminiError(
            f"Impossible de contacter l'API Gemini : {exc}", status_code=502
        ) from exc

    if resp.status_code != 200:
        detail = _extract_error_message(resp)
        raise GeminiError(
            f"L'API Gemini a renvoyé une erreur ({resp.status_code}) : {detail}",
            status_code=502,
        )

    return _extract_image(resp)


async def detect_door_bbox(
    user_image: bytes,
    user_image_mime: str,
    img_w: int,
    img_h: int,
) -> Optional[dict[str, int]]:
    """Localise la porte dans la photo via Gemini Flash (réponse texte seulement).

    Retourne {"x1": int, "y1": int, "x2": int, "y2": int} en pixels, ou None.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    prompt = (
        f"Image size: {img_w}x{img_h} pixels.\n"
        "Find the main front entrance door in this building photo.\n"
        "Return ONLY valid JSON (no other text):\n"
        '{"x1": <left_px>, "y1": <top_px>, "x2": <right_px>, "y2": <bottom_px>}\n'
        "Values are pixel coordinates of the door leaf bounding box "
        "(the door itself, not the surrounding frame or wall)."
    )

    parts = [
        {"text": prompt},
        _bytes_to_part(user_image, user_image_mime),
    ]

    detection_model = os.getenv("GEMINI_DETECTION_MODEL", "gemini-2.0-flash")
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"responseModalities": ["TEXT"]},
    }
    url = f"{API_BASE}/models/{detection_model}:generateContent"
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            return None
        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates:
            return None
        text = candidates[0]["content"]["parts"][0]["text"]

        match = _re.search(r"\{[^{}]+\}", text)
        if not match:
            return None
        bbox = _json.loads(match.group())

        if not all(k in bbox for k in ("x1", "y1", "x2", "y2")):
            return None

        result = {k: int(float(bbox[k])) for k in ("x1", "y1", "x2", "y2")}

        if result["x2"] <= result["x1"] or result["y2"] <= result["y1"]:
            return None
        door_area = (result["x2"] - result["x1"]) * (result["y2"] - result["y1"])
        if door_area < 0.01 * img_w * img_h:
            return None

        return result
    except Exception:
        return None


def _extract_error_message(resp: httpx.Response) -> str:
    try:
        data = resp.json()
        return data.get("error", {}).get("message", resp.text[:300])
    except Exception:  # noqa: BLE001 - on veut juste un message lisible
        return resp.text[:300]


def _extract_image(resp: httpx.Response) -> tuple[bytes, str]:
    try:
        data = resp.json()
    except Exception as exc:  # noqa: BLE001
        raise GeminiError(
            "Réponse illisible de l'API Gemini.", status_code=502
        ) from exc

    candidates = data.get("candidates") or []
    for candidate in candidates:
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inline_data") or part.get("inlineData")
            if inline and inline.get("data"):
                mime = inline.get("mime_type") or inline.get("mimeType", "image/png")
                try:
                    raw = base64.b64decode(inline["data"])
                except Exception as exc:  # noqa: BLE001
                    raise GeminiError(
                        "Image générée invalide.", status_code=502
                    ) from exc
                return raw, mime

    # Pas d'image : souvent un blocage de sécurité, on remonte la raison.
    reason = ""
    if candidates:
        reason = candidates[0].get("finishReason", "")
    block = data.get("promptFeedback", {}).get("blockReason", "")
    detail = block or reason or "aucune image renvoyée"
    raise GeminiError(
        f"L'IA n'a pas produit d'image ({detail}). Essayez une autre photo.",
        status_code=502,
    )
