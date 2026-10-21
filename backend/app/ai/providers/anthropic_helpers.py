"""Funciones puras de `AnthropicProvider` (US-007), sin dependencia del SDK.

Este módulo NO importa `anthropic`: solo transforma datos (mensajes, tools,
JSON, costos, reintentos). El único módulo que habla con el SDK es
`anthropic_provider.py` (regla no negociable #1 de CLAUDE.md, ADR-002).
"""

from __future__ import annotations

import base64
import json
import random
import re
from collections.abc import Mapping
from typing import Any

from app.ai.exceptions import InvalidResponseError
from app.ai.providers.base_provider import (
    CompletionRequest,
    StopReason,
    ToolCall,
    ToolResult,
)
from app.core.config import ModelPricing
from app.core.logging import get_logger

logger = get_logger(__name__)

JSON_MODE_INSTRUCTION = (
    "Responde ÚNICAMENTE con un objeto JSON válido. Sin texto antes o después, "
    "sin bloques de código markdown."
)
BACKOFF_BASE_SECONDS = 1.0

# Un único fence exterior: ```[etiqueta]<salto de línea><cuerpo>```, sin nada antes ni después.
_JSON_FENCE = re.compile(r"```[A-Za-z0-9_+-]*[ \t]*\n(.*?)\n?```", re.DOTALL)

# Firmas (magic bytes) de los formatos de imagen que acepta la API.
_IMAGE_SIGNATURES: tuple[tuple[bytes, str], ...] = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
)


def detect_image_media_type(image_bytes: bytes) -> str:
    """Detecta el media type por magic bytes; `ValueError` si el formato no se acepta."""
    for signature, media_type in _IMAGE_SIGNATURES:
        if image_bytes.startswith(signature):
            return media_type
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    raise ValueError("Formato de imagen no soportado (se aceptan PNG, JPEG, GIF y WEBP).")


def unwrap_and_validate_json(text: str) -> str:
    """Quita un único fence markdown exterior (si lo hay) y valida con `json.loads`."""
    candidate = text.strip()
    if candidate.startswith("```"):
        match = _JSON_FENCE.fullmatch(candidate)
        if match is None:
            raise InvalidResponseError(
                "json_mode=True pero la respuesta trae un bloque de código mal formado "
                "(sin cerrar, sin salto de línea o con texto alrededor)."
            )
        candidate = match.group(1).strip()
    try:
        json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise InvalidResponseError(
            "json_mode=True pero la respuesta de Claude no es JSON válido."
        ) from exc
    return candidate


def compute_cost(
    pricing: Mapping[str, ModelPricing], model: str, tokens_input: int, tokens_output: int
) -> float | None:
    """Costo en USD según la tabla configurada; `None` si el modelo no tiene precio."""
    price = pricing.get(model)
    if price is None:
        logger.warning("anthropic_pricing_missing", model=model)
        return None
    return (tokens_input * price.input_per_mtok + tokens_output * price.output_per_mtok) / 1_000_000


def map_stop_reason(stop_reason: str | None) -> StopReason:
    if stop_reason == "tool_use":
        return StopReason.TOOL_USE
    if stop_reason == "max_tokens":
        return StopReason.MAX_TOKENS
    return StopReason.END_TURN


def retry_delay(retry_after_header: str | None, attempt: int, cap_seconds: float) -> float:
    """`retry-after` del servidor si viene; si no, exponencial con jitter. Siempre con tope."""
    if retry_after_header is not None:
        try:
            return min(max(float(retry_after_header), 0.0), cap_seconds)
        except ValueError:
            pass  # formato fecha HTTP u otro: caer al backoff exponencial.
    exponential = BACKOFF_BASE_SECONDS * (2**attempt)
    jittered: float = exponential * random.uniform(0.5, 1.0)
    return min(jittered, cap_seconds)


def build_request_params(
    request: CompletionRequest,
    model: str,
    extra_messages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Traduce un `CompletionRequest` a los kwargs de `messages.create`.

    `temperature` no se envía y el thinking va desactivado (ver `complete()`).
    """
    system_parts: list[str] = []
    if request.system_prompt:
        system_parts.append(request.system_prompt)
    messages: list[dict[str, Any]] = []
    for m in request.messages:
        # La API solo admite user/assistant en `messages`: un "system" se pliega al system.
        if m.role == "system":
            system_parts.append(m.content)
        else:
            messages.append(
                {"role": "assistant" if m.role == "assistant" else "user", "content": m.content}
            )
    messages.extend(extra_messages or [])
    if request.json_mode:
        system_parts.append(JSON_MODE_INSTRUCTION)

    params: dict[str, Any] = {
        "model": model,
        "max_tokens": request.max_tokens,
        "messages": messages,
        "thinking": {"type": "disabled"},
    }
    if system_parts:
        params["system"] = [{"type": "text", "text": "\n\n".join(system_parts)}]
    if request.stop_sequences:
        params["stop_sequences"] = request.stop_sequences
    if request.tools:
        params["tools"] = [
            {"name": t.name, "description": t.description, "input_schema": t.input_schema}
            for t in request.tools
        ]
    return params


def build_tool_turn_messages(
    tool_calls: list[ToolCall], tool_results: list[ToolResult]
) -> list[dict[str, Any]]:
    """Turnos assistant (tool_use) + user (tool_result) para continuar tras ejecutar tools."""
    call_ids = {c.id for c in tool_calls}
    result_ids = {r.tool_call_id for r in tool_results}
    if call_ids != result_ids or len(tool_results) != len(result_ids):
        raise ValueError(
            "Cada ToolCall debe tener exactamente un ToolResult con su mismo id "
            f"(calls={sorted(call_ids)}, results={sorted(result_ids)})."
        )
    tool_use_blocks = [
        {"type": "tool_use", "id": c.id, "name": c.name, "input": c.arguments} for c in tool_calls
    ]
    tool_result_blocks: list[dict[str, Any]] = []
    for r in tool_results:
        block: dict[str, Any] = {
            "type": "tool_result",
            "tool_use_id": r.tool_call_id,
            "content": r.content,
        }
        if r.is_error:
            block["is_error"] = True
        tool_result_blocks.append(block)
    return [
        {"role": "assistant", "content": tool_use_blocks},
        {"role": "user", "content": tool_result_blocks},
    ]


def build_image_params(model: str, image_bytes: bytes, prompt: str) -> dict[str, Any]:
    """kwargs de `messages.create` para analizar una imagen (tier VISION)."""
    return {
        "model": model,
        "max_tokens": 1024,
        "thinking": {"type": "disabled"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": detect_image_media_type(image_bytes),
                            "data": base64.b64encode(image_bytes).decode("ascii"),
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }
