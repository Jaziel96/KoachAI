"""Tests de `GET /health` (US-003)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from app.main import app


@asynccontextmanager
async def _fake_session_ok(user_id: str | None = None) -> AsyncIterator[AsyncMock]:
    session = AsyncMock()
    yield session


@asynccontextmanager
async def _fake_session_down(user_id: str | None = None) -> AsyncIterator[AsyncMock]:
    raise ConnectionError("db unreachable")
    yield  # pragma: no cover - nunca se alcanza, mantiene la firma de generador


@patch("app.api.health.get_session", _fake_session_ok)
@patch("app.api.health.redis.from_url")
async def test_health_returns_200_when_all_up(mock_from_url: AsyncMock) -> None:
    mock_redis = AsyncMock()
    mock_from_url.return_value = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["checks"]["database"]["status"] == "up"
    assert body["checks"]["redis"]["status"] == "up"


@patch("app.api.health.get_session", _fake_session_down)
@patch("app.api.health.redis.from_url")
async def test_health_returns_503_when_database_down(mock_from_url: AsyncMock) -> None:
    mock_redis = AsyncMock()
    mock_from_url.return_value = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unhealthy"
    assert body["checks"]["database"]["status"] == "down"


@patch("app.api.health.get_session", _fake_session_ok)
@patch("app.api.health.redis.from_url")
async def test_health_includes_request_id_header(mock_from_url: AsyncMock) -> None:
    mock_redis = AsyncMock()
    mock_from_url.return_value = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert "X-Request-ID" in response.headers


async def test_unhandled_exception_returns_500_without_stack_trace() -> None:
    @app.get("/__boom")
    async def _boom() -> None:
        raise RuntimeError("secreto interno que no debe salir")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/__boom")

    assert response.status_code == 500
    body = response.json()
    assert "secreto interno" not in str(body)
    assert body == {"detail": "Ocurrió un error interno. Ya fue registrado."}
