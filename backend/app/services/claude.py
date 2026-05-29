import asyncio
import logging

import anthropic

from app.core.config import settings
from app.prompts.plan_inicial import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_MODEL = "claude-sonnet-4-20250514"
_MAX_TOKENS = 2048
_RETRY_DELAY_SECONDS = 2


def _call_api(prompt: str) -> str:
    """Llamada síncrona al SDK de Anthropic (se usa dentro de asyncio.to_thread)."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


async def generate_plan(prompt: str) -> str:
    """Genera texto con Claude. Reintenta una vez tras 2s si falla (FA-01, FA-02)."""
    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            return await asyncio.to_thread(_call_api, prompt)
        except Exception as exc:
            last_exc = exc
            if attempt == 0:
                logger.warning(f"Claude API intento 1 falló: {exc} — reintentando en {_RETRY_DELAY_SECONDS}s")
                await asyncio.sleep(_RETRY_DELAY_SECONDS)
            else:
                logger.error(f"Claude API intento 2 falló: {exc}")
    raise last_exc
