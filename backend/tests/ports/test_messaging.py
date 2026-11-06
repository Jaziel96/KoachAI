"""Tests de la interface de mensajería (US-015)."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.ports.messaging import (
    Button,
    IncomingMessage,
    MessageType,
    MessagingChannel,
)
from tests.ports.mock_channel import MockMessagingChannel

APP_DIR = Path(__file__).resolve().parents[2] / "app"
# Únicos lugares donde puede vivir código específico de WhatsApp (CA-2).
PERMITIDOS = ("ports", "adapters")


def _imports(source: Path) -> set[str]:
    arbol = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    modulos: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module)
    return modulos


def test_message_type_tiene_los_cinco_valores() -> None:
    assert {m.name for m in MessageType} == {
        "TEXT",
        "AUDIO",
        "IMAGE",
        "BUTTON_REPLY",
        "DOCUMENT",
    }


def test_interface_no_se_puede_instanciar_incompleta() -> None:
    class Incompleto(MessagingChannel):
        async def send_text(self, to: str, text: str) -> str:
            return "x"

    with pytest.raises(TypeError):
        Incompleto()  # type: ignore[abstract]


def test_interface_declara_los_cuatro_metodos_abstractos() -> None:
    assert MessagingChannel.__abstractmethods__ == {
        "send_text",
        "send_buttons",
        "send_document",
        "send_template",
    }


async def test_ca1_ca3_mock_cumple_el_contrato_completo() -> None:
    canal: MessagingChannel = MockMessagingChannel()

    ids = [
        await canal.send_text("5215512345678", "Hola"),
        await canal.send_buttons(
            "5215512345678", "¿Qué prefieres?", [Button(id="a", title="Opción A")]
        ),
        await canal.send_document("5215512345678", "https://x.test/doc.pdf", None),
        await canal.send_template("5215512345678", "bienvenida", {"nombre": "Ana"}),
    ]

    assert all(isinstance(i, str) and i for i in ids)
    assert len(set(ids)) == 4
    assert isinstance(canal, MockMessagingChannel)
    assert [kind for kind, _, _ in canal.sent] == [
        "text",
        "buttons",
        "document",
        "template",
    ]
    assert canal.sent[1][2]["buttons"] == [Button(id="a", title="Opción A")]
    assert canal.sent[2][2]["caption"] is None


def test_incoming_message_agnostico_de_canal() -> None:
    msg = IncomingMessage(
        channel="app",
        from_id="user-uuid",
        message_id="m1",
        type=MessageType.BUTTON_REPLY,
        button_payload="opcion_a",
        timestamp=datetime.now(UTC),
    )
    assert msg.text is None
    assert msg.media_url is None
    assert msg.button_payload == "opcion_a"


def test_ca2_ports_no_importa_nada_de_whatsapp() -> None:
    modulos = _imports(APP_DIR / "ports" / "messaging.py")
    assert not any("whatsapp" in m.lower() for m in modulos)


def test_ca2_nada_fuera_de_ports_y_adapters_depende_de_whatsapp() -> None:
    """Listo para cuando exista lógica de negocio (services/, domain/, ai/...)."""
    ofensores: list[str] = []
    for archivo in APP_DIR.rglob("*.py"):
        if archivo.relative_to(APP_DIR).parts[0] in PERMITIDOS:
            continue
        if any("whatsapp" in m.lower() for m in _imports(archivo)):
            ofensores.append(str(archivo.relative_to(APP_DIR)))
    assert ofensores == []


def _mensaje() -> IncomingMessage:
    return IncomingMessage(
        channel="whatsapp",
        from_id="5215512345678",
        message_id="m1",
        type=MessageType.TEXT,
        timestamp=datetime.now(UTC),
        text="me siento mal",
        media_url="https://x.test/foto.jpg",
    )


def test_repr_de_incoming_message_no_filtra_pii() -> None:
    """El repr (logs, tracebacks) no debe volcar teléfono, texto ni media_url."""
    salida = repr(_mensaje())
    assert "5215512345678" not in salida
    assert "me siento mal" not in salida
    assert "foto.jpg" not in salida


def test_incoming_message_es_inmutable() -> None:
    """Un mensaje ya revisado por el screening de crisis no puede alterarse."""
    msg = _mensaje()
    with pytest.raises(FrozenInstanceError):
        msg.text = "otro texto"  # type: ignore[misc]


def test_button_es_inmutable() -> None:
    boton = Button(id="a", title="Opción A")
    with pytest.raises(FrozenInstanceError):
        boton.title = "otra"  # type: ignore[misc]
