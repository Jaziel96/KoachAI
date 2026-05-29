"""
Tests de US-002: detección de usuario y onboarding conversacional.
Cubre CA-01 a CA-08, CE-02 y FA-04.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.messages.es_mx import (
    BIENVENIDA_Y_CONSENTIMIENTO,
    CONSENTIMIENTO_RECHAZADO,
    DEMASIADOS_INTENTOS,
    ERROR_EDAD_MINIMA,
    PREGUNTAS,
    RESPUESTA_INVALIDA,
)
from app.services.onboarding import (
    _complete_onboarding,
    _validate_answer,
    handle_onboarding,
)
from app.services.whatsapp import handle_message

PHONE = "521234567890"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _state(paso: int, datos: dict | None = None, intentos: int = 0) -> dict:
    return {"paso_actual": paso, "datos_parciales": datos or {}, "intentos_paso": intentos}


def _patch_onboarding(*patches):
    """Contexto para parchear helpers internos del módulo onboarding."""
    return patches


# ---------------------------------------------------------------------------
# CA-01: Usuario nuevo recibe bienvenida y solicitud de consentimiento
# ---------------------------------------------------------------------------


async def test_new_user_gets_welcome_and_consent():
    with (
        patch("app.services.onboarding._load_state", return_value=None),
        patch("app.services.onboarding._create_state", new_callable=AsyncMock) as mock_create,
        patch("app.services.onboarding.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await handle_onboarding(PHONE, "hola")
        mock_create.assert_called_once_with(PHONE)
        mock_send.assert_called_once_with(PHONE, BIENVENIDA_Y_CONSENTIMIENTO)


# ---------------------------------------------------------------------------
# CA-02: Rechazo de consentimiento — ningún dato guardado, mensaje de cierre
# ---------------------------------------------------------------------------


async def test_consent_rejected_deletes_state_and_sends_closing():
    with (
        patch("app.services.onboarding._load_state", return_value=_state(0)),
        patch("app.services.onboarding._delete_state", new_callable=AsyncMock) as mock_del,
        patch("app.services.onboarding.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await handle_onboarding(PHONE, "no")
        mock_del.assert_called_once_with(PHONE)
        mock_send.assert_called_once_with(PHONE, CONSENTIMIENTO_RECHAZADO)


# ---------------------------------------------------------------------------
# CA-03: Aceptación de consentimiento → pregunta 1 + estado guardado en paso 1
# ---------------------------------------------------------------------------


async def test_consent_accepted_saves_state_and_sends_question_1():
    with (
        patch("app.services.onboarding._load_state", return_value=_state(0)),
        patch("app.services.onboarding._save_state", new_callable=AsyncMock) as mock_save,
        patch("app.services.onboarding.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await handle_onboarding(PHONE, "sí")
        mock_save.assert_called_once_with(PHONE, 1, {"consintio": True}, 0)
        mock_send.assert_called_once_with(PHONE, PREGUNTAS[1])


# ---------------------------------------------------------------------------
# CA-04: Respuesta inválida → mensaje de ayuda, sin avanzar de paso
# ---------------------------------------------------------------------------


async def test_invalid_age_sends_error_and_increments_attempts():
    with (
        patch("app.services.onboarding._load_state", return_value=_state(2, {"nombre": "Juan"})),
        patch("app.services.onboarding._save_state", new_callable=AsyncMock) as mock_save,
        patch("app.services.onboarding.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await handle_onboarding(PHONE, "no se cuántos")
        mock_save.assert_called_once_with(PHONE, 2, {"nombre": "Juan"}, 1)
        mock_send.assert_called_once_with(PHONE, RESPUESTA_INVALIDA[2])


# ---------------------------------------------------------------------------
# CA-05: Las 7 preguntas completas → _complete_onboarding llamado con datos correctos
# ---------------------------------------------------------------------------


async def test_all_7_steps_completed_calls_complete():
    datos = {
        "consintio": True, "nombre": "Juan", "edad": 28,
        "peso_kg": 70.0, "talla_cm": 175, "genero": "hombre", "meta": "bajar de peso",
    }
    with (
        patch("app.services.onboarding._load_state", return_value=_state(7, datos)),
        patch("app.services.onboarding._complete_onboarding", new_callable=AsyncMock) as mock_comp,
    ):
        await handle_onboarding(PHONE, "ninguna")
        mock_comp.assert_called_once()
        call_datos = mock_comp.call_args[0][1]
        assert call_datos["alergias"] == "ninguna"
        assert call_datos["nombre"] == "Juan"


async def test_complete_onboarding_sends_confirmation_message():
    datos = {
        "consintio": True, "nombre": "María", "edad": 30, "peso_kg": 60.0,
        "talla_cm": 165, "genero": "mujer", "meta": "comer mejor", "alergias": "lactosa",
    }
    insert_result = MagicMock(data=[{"id": "uuid-test"}])

    with (
        patch("app.services.onboarding.asyncio.to_thread", new_callable=AsyncMock,
              return_value=insert_result),
        patch("app.services.onboarding.get_client"),
        patch("app.services.onboarding._delete_state", new_callable=AsyncMock),
        patch("app.services.onboarding.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await _complete_onboarding(PHONE, datos)
        mock_send.assert_called_once()
        assert "María" in mock_send.call_args[0][1]


# ---------------------------------------------------------------------------
# CA-06: Usuario abandona a mitad y retoma desde donde dejó
# ---------------------------------------------------------------------------


async def test_abandoned_user_resumes_from_last_step():
    datos = {"consintio": True, "nombre": "Juan", "edad": 28}
    with (
        patch("app.services.onboarding._load_state", return_value=_state(3, datos)),
        patch("app.services.onboarding._save_state", new_callable=AsyncMock) as mock_save,
        patch("app.services.onboarding.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await handle_onboarding(PHONE, "75")
        # Debe avanzar al paso 4 con el peso guardado
        saved_datos = mock_save.call_args[0][2]
        assert saved_datos["peso_kg"] == 75.0
        mock_send.assert_called_once_with(PHONE, PREGUNTAS[4])


# ---------------------------------------------------------------------------
# CA-07: Menor de 13 años — excluido, sin guardar datos
# ---------------------------------------------------------------------------


async def test_under_13_excluded():
    with (
        patch("app.services.onboarding._load_state",
              return_value=_state(2, {"nombre": "Niño"})),
        patch("app.services.onboarding._delete_state", new_callable=AsyncMock) as mock_del,
        patch("app.services.onboarding.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await handle_onboarding(PHONE, "10")
        mock_del.assert_called_once_with(PHONE)
        mock_send.assert_called_once_with(PHONE, ERROR_EDAD_MINIMA)


# ---------------------------------------------------------------------------
# CA-08: Usuario existente recibe "¡Hola de nuevo!"
# ---------------------------------------------------------------------------


async def test_existing_user_gets_greeting():
    with (
        patch("app.services.whatsapp._buscar_usuario",
              new_callable=AsyncMock, return_value={"nombre": "Carlos"}),
        patch("app.services.whatsapp.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await handle_message(PHONE, "hola")
        mock_send.assert_called_once()
        assert "Carlos" in mock_send.call_args[0][1]


# ---------------------------------------------------------------------------
# FA-04: Después de 3 intentos inválidos → sugerir "reiniciar"
# ---------------------------------------------------------------------------


async def test_3_invalid_attempts_suggests_reiniciar():
    with (
        patch("app.services.onboarding._load_state",
              return_value=_state(2, {"nombre": "Ana"}, intentos=2)),
        patch("app.services.onboarding._save_state", new_callable=AsyncMock),
        patch("app.services.onboarding.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await handle_onboarding(PHONE, "texto inválido")
        mock_send.assert_called_once_with(PHONE, DEMASIADOS_INTENTOS)


# ---------------------------------------------------------------------------
# Tests de _validate_answer (unidades)
# ---------------------------------------------------------------------------


def test_validate_name_valid():
    ok, val, err = _validate_answer(1, "juan pablo")
    assert ok and val == "Juan Pablo" and err is None


def test_validate_age_valid():
    ok, val, err = _validate_answer(2, "25")
    assert ok and val == 25 and err is None


def test_validate_age_under_13():
    ok, _, err = _validate_answer(2, "10")
    assert not ok and err == "edad_minima"


def test_validate_weight_normal():
    ok, val, err = _validate_answer(3, "75.5")
    assert ok and val == 75.5 and err is None


def test_validate_weight_out_of_range():
    ok, val, err = _validate_answer(3, "500")
    assert not ok and err == "peso_fuera_de_rango" and val == 500.0


def test_validate_height_valid():
    ok, val, err = _validate_answer(4, "170 cm")
    assert ok and val == 170 and err is None


def test_validate_gender_valid():
    ok, val, err = _validate_answer(5, "mujer")
    assert ok and val == "mujer" and err is None


def test_validate_gender_invalid():
    ok, _, err = _validate_answer(5, "femenino")
    assert not ok and err == "invalid"


def test_validate_goal_valid():
    ok, val, err = _validate_answer(6, "bajar de peso")
    assert ok and val == "bajar de peso" and err is None


def test_validate_goal_accent_free():
    ok, val, err = _validate_answer(6, "mas energia")
    assert ok and val == "más energía" and err is None


def test_validate_allergies_valid():
    ok, val, err = _validate_answer(7, "ninguna")
    assert ok and val == "ninguna" and err is None
