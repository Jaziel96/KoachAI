"""Endpoint de salud del sistema (US-003).

Verifica DB y Redis con una operación real y de bajo costo. El check de IA
**no** invoca ningún SDK de proveedor directamente (regla #1 de CLAUDE.md:
ningún import de SDKs de IA fuera de `app/ai/`, capa que todavía no existe —
esa abstracción llega en M2, US-006 en adelante). Por ahora solo reporta si
hay credenciales configuradas para cada proveedor, sin llamar a la API real.
"""

import time
from typing import Literal

import redis.asyncio as redis
from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app.adapters.persistence.db import get_session
from app.core.config import get_settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

CheckStatus = Literal["up", "down", "not_configured"]
OverallStatus = Literal["healthy", "degraded", "unhealthy"]


class DependencyCheck(BaseModel):
    """Resultado del chequeo de una dependencia individual."""

    status: CheckStatus
    latency_ms: float | None = None
    provider: str | None = None
    detail: str | None = None


class HealthResponse(BaseModel):
    """Contrato de respuesta de `GET /health` (ver spec US-003)."""

    status: OverallStatus
    version: str
    checks: dict[str, DependencyCheck]


async def _check_database() -> DependencyCheck:
    start = time.perf_counter()
    try:
        async with get_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - un check de salud no debe propagar
        logger.error("health_check_database_failed", error=str(exc))
        return DependencyCheck(status="down", detail="No se pudo conectar a la base de datos")
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    return DependencyCheck(status="up", latency_ms=latency_ms)


async def _check_redis() -> DependencyCheck:
    settings = get_settings()
    start = time.perf_counter()
    client: redis.Redis = redis.from_url(str(settings.REDIS_URL))  # type: ignore[no-untyped-call]
    try:
        await client.ping()
    except Exception as exc:  # noqa: BLE001 - un check de salud no debe propagar
        logger.error("health_check_redis_failed", error=str(exc))
        return DependencyCheck(status="down", detail="No se pudo conectar a Redis")
    finally:
        await client.aclose()
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    return DependencyCheck(status="up", latency_ms=latency_ms)


def _check_ai_provider(*, provider: str, api_key_set: bool) -> DependencyCheck:
    if not api_key_set:
        return DependencyCheck(status="not_configured", provider=provider)
    return DependencyCheck(status="up", provider=provider)


@router.get("/health", response_model=HealthResponse)
async def health(response: Response) -> HealthResponse:
    """Reporta el estado de las dependencias críticas del sistema."""
    settings = get_settings()

    db_check = await _check_database()
    redis_check = await _check_redis()
    ai_smart_check = _check_ai_provider(
        provider=settings.AI_SMART_PROVIDER,
        api_key_set=settings.ANTHROPIC_API_KEY is not None,
    )
    ai_fast_check = _check_ai_provider(
        provider=settings.AI_FAST_PROVIDER,
        api_key_set=settings.GEMINI_API_KEY is not None,
    )

    checks = {
        "database": db_check,
        "redis": redis_check,
        "ai_smart": ai_smart_check,
        "ai_fast": ai_fast_check,
    }

    critical_down = db_check.status == "down" or redis_check.status == "down"
    overall: OverallStatus
    if critical_down:
        overall = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif any(c.status == "not_configured" for c in (ai_smart_check, ai_fast_check)):
        overall = "degraded"
    else:
        overall = "healthy"

    return HealthResponse(status=overall, version="0.1.0", checks=checks)
