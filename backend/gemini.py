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
import os
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
    """Construit l'instruction d'édition envoyée à l'IA.

    Objectif : que l'IA ne modifie QUE la porte et laisse le reste de la photo
    rigoureusement intact (cadrage, perspective, lumière, pixels alentour).
    """
    return (
        "You are a professional architectural photo retoucher. You will edit "
        "the FIRST image, which is a real photograph of a building facade with "
        "an existing front entrance door.\n\n"
        "TASK: replace ONLY the existing entrance door — the door leaf and its "
        "own glazing/hardware — with a new door described below.\n\n"
        "ABSOLUTE REQUIREMENTS (very important):\n"
        "- Return THE SAME photograph: identical framing, crop, zoom, aspect "
        "ratio, resolution, camera angle and perspective.\n"
        "- Every pixel that is NOT the door must stay EXACTLY as in the "
        "original: the surrounding wall, the door frame/casing and threshold, "
        "the ground, steps, plants, windows, other doors, sky, signage, "
        "people, reflections — all unchanged.\n"
        "- Do NOT move, rotate, rescale, recolor, relight or restyle anything "
        "except the door itself. Do not crop or zoom. Do not add or remove "
        "objects.\n"
        "- Keep the door in the exact same position and size as the original "
        "door opening.\n"
        "- Match the new door's lighting, shadows, white balance and "
        "perspective to the original scene so the edit is invisible and "
        "photorealistic.\n\n"
        f"NEW DOOR TO PUT: {door_prompt} (style name: \"{door_name}\").\n"
        "If a SECOND image is provided, copy the door's design, materials and "
        "colour from it, but IGNORE that reference's background and framing.\n\n"
        "Output ONLY the edited photograph, with the exact same dimensions as "
        "the first input image."
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
