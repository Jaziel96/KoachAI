"""Integración de US-009 contra la API real de Anthropic.

La lógica de selección/fallback/tools/logs del router ya está cubierta con
providers ficticios en `test_router.py` — lo único que falta verificar aquí
es que `AIRouter.from_settings()` arma correctamente un `AnthropicProvider`
real y que una llamada completa funciona de punta a punta a través del
router (no directo al provider, que ya lo cubre US-007).

Se omite si no hay `ANTHROPIC_API_KEY` real (en el entorno o en `backend/.env`).
"""

from __future__ import annotations

import pytest
from pydantic import SecretStr

from app.ai.providers.base_provider import CompletionRequest, Message, ModelTier
from app.ai.router import AIRouter
from app.core.config import get_settings

pytestmark = pytest.mark.integration

_PLACEHOLDER_KEYS = {"", "sk-ant-...", "sk-ant-"}


def _tiene_key_real() -> bool:
    key: SecretStr | None = get_settings().ANTHROPIC_API_KEY
    return key is not None and key.get_secret_value() not in _PLACEHOLDER_KEYS


@pytest.mark.skipif(not _tiene_key_real(), reason="Sin ANTHROPIC_API_KEY real.")
@pytest.mark.asyncio
async def test_router_completa_end_to_end_contra_anthropic_real() -> None:
    router = AIRouter.from_settings(get_settings())

    respuesta = await router.complete(
        CompletionRequest(messages=[Message(role="user", content="Responde solo: OK")]),
        tier=ModelTier.FAST,
    )

    assert respuesta.provider == "anthropic"
    assert respuesta.content
    assert respuesta.tokens_output > 0
