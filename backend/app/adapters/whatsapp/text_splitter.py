"""Split de mensajes que exceden el límite de WhatsApp (US-017, RF-5)."""

from __future__ import annotations

MAX_LENGTH = 4096


def split_text(text: str, limit: int = MAX_LENGTH) -> list[str]:
    """Divide `text` en partes de a lo sumo `limit` caracteres, sin cortar palabras.

    Corta preferentemente en salto de línea, luego en espacio. Solo parte una
    palabra por la mitad si ella sola excede `limit`. Texto vacío → lista vacía.
    """
    rest = text.strip()
    parts: list[str] = []
    while len(rest) > limit:
        window = rest[: limit + 1]
        cut = window.rfind("\n")
        if cut <= 0:
            cut = window.rfind(" ")
        if cut <= 0:
            cut = limit
        parts.append(rest[:cut].rstrip())
        rest = rest[cut:].lstrip()
    if rest:
        parts.append(rest)
    return parts
