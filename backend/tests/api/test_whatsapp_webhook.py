"""Tests de `/webhooks/whatsapp` (US-016, CA-1 a CA-4)."""

import hashlib
import hmac
import json
import time
from collections.abc import Iterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.webhooks.whatsapp import get_deduplicator, get_message_queue
from app.main import app
from tests.ports.fakes import FakeDeduplicator, FakeQueue

SECRET = "test-app-secret"  # fijado en tests/conftest.py
VERIFY = "test-verify-token"
BODY = json.dumps(
    {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "5215512345678",
                                    "id": "wamid.1",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": "hola"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
).encode()


def _firma(body: bytes) -> dict[str, str]:
    digest = hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return {"X-Hub-Signature-256": f"sha256={digest}", "Content-Type": "application/json"}


@pytest.fixture
def fakes() -> Iterator[tuple[FakeDeduplicator, FakeQueue]]:
    dedup, queue = FakeDeduplicator(), FakeQueue()
    app.dependency_overrides[get_deduplicator] = lambda: dedup
    app.dependency_overrides[get_message_queue] = lambda: queue
    yield dedup, queue
    app.dependency_overrides.clear()


def _client(raise_app_exceptions: bool = True) -> AsyncClient:
    transport = ASGITransport(app=app, raise_app_exceptions=raise_app_exceptions)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_ca1_verificacion_de_meta() -> None:
    params = {"hub.mode": "subscribe", "hub.verify_token": VERIFY, "hub.challenge": "12345"}
    async with _client() as c:
        r = await c.get("/webhooks/whatsapp", params=params)
    assert r.status_code == 200
    assert r.text == "12345"


async def test_verificacion_con_token_incorrecto_es_403() -> None:
    params = {"hub.mode": "subscribe", "hub.verify_token": "malo", "hub.challenge": "1"}
    async with _client() as c:
        r = await c.get("/webhooks/whatsapp", params=params)
    assert r.status_code == 403


async def test_ca2_firma_invalida_es_403_y_no_encola(
    fakes: tuple[FakeDeduplicator, FakeQueue],
) -> None:
    _, queue = fakes
    async with _client() as c:
        r = await c.post(
            "/webhooks/whatsapp", content=BODY, headers={"X-Hub-Signature-256": "sha256=00"}
        )
        sin_firma = await c.post("/webhooks/whatsapp", content=BODY)
    assert r.status_code == 403
    assert sin_firma.status_code == 403
    assert queue.messages == []


async def test_mensaje_valido_se_encola_y_responde_200(
    fakes: tuple[FakeDeduplicator, FakeQueue],
) -> None:
    _, queue = fakes
    async with _client() as c:
        r = await c.post("/webhooks/whatsapp", content=BODY, headers=_firma(BODY))
    assert r.status_code == 200
    assert [m.message_id for m in queue.messages] == ["wamid.1"]
    assert queue.messages[0].text == "hola"


async def test_ca3_mensaje_duplicado_se_ignora(
    fakes: tuple[FakeDeduplicator, FakeQueue],
) -> None:
    _, queue = fakes
    async with _client() as c:
        r1 = await c.post("/webhooks/whatsapp", content=BODY, headers=_firma(BODY))
        r2 = await c.post("/webhooks/whatsapp", content=BODY, headers=_firma(BODY))
    assert r1.status_code == r2.status_code == 200
    assert len(queue.messages) == 1


async def test_ca4_responde_en_menos_de_500ms(
    fakes: tuple[FakeDeduplicator, FakeQueue],
) -> None:
    async with _client() as c:
        inicio = time.perf_counter()
        await c.post("/webhooks/whatsapp", content=BODY, headers=_firma(BODY))
    assert time.perf_counter() - inicio < 0.5


async def test_si_falla_la_cola_se_libera_el_mensaje_para_el_reintento_de_meta() -> None:
    dedup, queue = FakeDeduplicator(), FakeQueue(fail=True)
    app.dependency_overrides[get_deduplicator] = lambda: dedup
    app.dependency_overrides[get_message_queue] = lambda: queue
    try:
        async with _client(raise_app_exceptions=False) as c:
            r = await c.post("/webhooks/whatsapp", content=BODY, headers=_firma(BODY))
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 500
    assert "wamid.1" not in dedup.seen


async def test_cuerpo_firmado_pero_no_json_es_400(
    fakes: tuple[FakeDeduplicator, FakeQueue],
) -> None:
    cuerpo = b"no es json"
    async with _client() as c:
        r = await c.post("/webhooks/whatsapp", content=cuerpo, headers=_firma(cuerpo))
    assert r.status_code == 400


async def test_cuerpo_demasiado_grande_es_413(
    fakes: tuple[FakeDeduplicator, FakeQueue],
) -> None:
    grande = b"x" * 1_000_001
    async with _client() as c:
        r = await c.post("/webhooks/whatsapp", content=grande, headers=_firma(grande))
    assert r.status_code == 413
