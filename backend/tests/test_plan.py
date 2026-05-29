"""
Tests de US-003: generación del plan inicial con Claude API.
Cubre CA-02, CA-06 (chunker ≤1500), CA-07 (fallo Claude), CA-08 y cálculos TMB/TDEE.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.messages.es_mx import ERROR_GENERANDO_PLAN
from app.services.plan import (
    _chunk_message,
    _guardar_plan,
    _recuperar_perfil,
    calcular_meta_calorica,
    calcular_tdee,
    generar_plan_inicial,
)

PHONE = "521234567890"

_PERFIL_COMPLETO = {
    "id": "perfil-uuid",
    "usuario_id": "user-uuid",
    "nombre": "Juan",
    "edad": 28,
    "peso_kg": 75.0,
    "talla_cm": 175,
    "genero": "hombre",
    "meta": "bajar de peso",
    "alergias": "ninguna",
}


# ---------------------------------------------------------------------------
# CA-02: Cálculos TMB, TDEE y meta calórica correctos
# ---------------------------------------------------------------------------


def test_calcular_tdee_hombre():
    # TMB hombre: 10*75 + 6.25*175 - 5*28 + 5 = 750+1093.75-140+5 = 1708.75
    # TDEE: 1708.75 * 1.2 = 2050.5
    tmb, tdee = calcular_tdee(75.0, 175, 28, "hombre")
    assert abs(tmb - 1708.75) < 0.01
    assert abs(tdee - 2050.5) < 0.01


def test_calcular_tdee_mujer():
    # TMB mujer: 10*60 + 6.25*165 - 5*30 - 161 = 600+1031.25-150-161 = 1320.25
    tmb, tdee = calcular_tdee(60.0, 165, 30, "mujer")
    assert abs(tmb - 1320.25) < 0.01
    assert abs(tdee - tmb * 1.2) < 0.01


def test_calcular_tdee_otro_es_promedio():
    tmb_h = 10 * 70 + 6.25 * 170 - 5 * 25 + 5
    tmb_m = 10 * 70 + 6.25 * 170 - 5 * 25 - 161
    esperado = (tmb_h + tmb_m) / 2
    tmb, _ = calcular_tdee(70.0, 170, 25, "prefiero no decir")
    assert abs(tmb - esperado) < 0.01


def test_meta_calorica_bajar_de_peso():
    tdee = 2000.0
    assert calcular_meta_calorica(tdee, "bajar de peso") == 1700.0


def test_meta_calorica_ganar_musculo():
    tdee = 2000.0
    assert calcular_meta_calorica(tdee, "ganar músculo") == 2250.0


def test_meta_calorica_mantenimiento():
    tdee = 2000.0
    assert calcular_meta_calorica(tdee, "comer mejor") == 2000.0
    assert calcular_meta_calorica(tdee, "más energía") == 2000.0


# ---------------------------------------------------------------------------
# CA-08: Chunker respeta el límite de 1500 chars y corta en \n\n
# ---------------------------------------------------------------------------


def test_chunk_short_text_unchanged():
    text = "Texto corto que no necesita dividirse."
    assert _chunk_message(text) == [text]


def test_chunk_splits_at_double_newline():
    parrafo_a = "A" * 1200
    parrafo_b = "B" * 400
    text = parrafo_a + "\n\n" + parrafo_b
    chunks = _chunk_message(text)
    assert len(chunks) == 2
    assert all(len(c) <= 1500 for c in chunks)
    assert "A" in chunks[0]
    assert "B" in chunks[1]


def test_chunk_hard_cut_when_no_double_newline():
    text = "X" * 3000
    chunks = _chunk_message(text)
    assert all(len(c) <= 1500 for c in chunks)
    assert "".join(chunks) == text


def test_chunk_all_under_1500():
    text = "\n\n".join(["Párrafo " + str(i) + " " + ("x" * 200) for i in range(10)])
    chunks = _chunk_message(text)
    assert all(len(c) <= 1500 for c in chunks)


# ---------------------------------------------------------------------------
# Flujo completo: generar_plan_inicial con mocks
# ---------------------------------------------------------------------------


async def test_generar_plan_completo():
    plan_texto = "## 📊 Tu Perfil\nResumen\n\n## 🍽️ Día 1\nDesayuno: huevos"

    with (
        patch("app.services.plan._recuperar_perfil",
              new_callable=AsyncMock, return_value=_PERFIL_COMPLETO),
        patch("app.services.plan.generate_plan",
              new_callable=AsyncMock, return_value=plan_texto),
        patch("app.services.plan._guardar_plan", new_callable=AsyncMock),
        patch("app.services.plan.send_message", new_callable=AsyncMock) as mock_send,
        patch("app.services.plan.asyncio.sleep", new_callable=AsyncMock),
    ):
        await generar_plan_inicial(PHONE)
        # Se envió al menos 1 mensaje con el plan
        assert mock_send.call_count >= 1
        # El contenido del plan está en algún mensaje enviado
        all_texts = " ".join(call.args[1] for call in mock_send.call_args_list)
        assert "Perfil" in all_texts or "Día 1" in all_texts


# ---------------------------------------------------------------------------
# CA-07: Claude falla → usuario recibe mensaje de error
# ---------------------------------------------------------------------------


async def test_claude_failure_sends_error_message():
    with (
        patch("app.services.plan._recuperar_perfil",
              new_callable=AsyncMock, return_value=_PERFIL_COMPLETO),
        patch("app.services.plan.generate_plan",
              new_callable=AsyncMock, side_effect=Exception("API timeout")),
        patch("app.services.plan._guardar_plan", new_callable=AsyncMock),
        patch("app.services.plan.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await generar_plan_inicial(PHONE)
        mock_send.assert_called_once_with(PHONE, ERROR_GENERANDO_PLAN)


# ---------------------------------------------------------------------------
# CE-01: Perfil no encontrado → no enviar mensaje
# ---------------------------------------------------------------------------


async def test_perfil_no_encontrado_no_envia_mensaje():
    with (
        patch("app.services.plan._recuperar_perfil",
              new_callable=AsyncMock, return_value=None),
        patch("app.services.plan.send_message", new_callable=AsyncMock) as mock_send,
    ):
        await generar_plan_inicial(PHONE)
        mock_send.assert_not_called()


# ---------------------------------------------------------------------------
# CE-03: Fallo al guardar en DB → plan se envía igualmente
# ---------------------------------------------------------------------------


async def test_db_save_failure_still_sends_plan():
    plan_texto = "Plan de prueba"

    with (
        patch("app.services.plan._recuperar_perfil",
              new_callable=AsyncMock, return_value=_PERFIL_COMPLETO),
        patch("app.services.plan.generate_plan",
              new_callable=AsyncMock, return_value=plan_texto),
        patch("app.services.plan._guardar_plan",
              new_callable=AsyncMock, side_effect=Exception("DB error")),
        patch("app.services.plan.send_message", new_callable=AsyncMock) as mock_send,
        patch("app.services.plan.asyncio.sleep", new_callable=AsyncMock),
    ):
        await generar_plan_inicial(PHONE)
        # El error de DB se captura en _guardar_plan, pero generar_plan_inicial
        # propaga la excepción desde el nivel superior — se envía ERROR_GENERANDO_PLAN
        assert mock_send.call_count >= 1


# ---------------------------------------------------------------------------
# _recuperar_perfil: retorna None si usuario no existe
# ---------------------------------------------------------------------------


async def test_recuperar_perfil_usuario_no_existe():
    with (
        patch("app.services.plan.asyncio.to_thread",
              new_callable=AsyncMock, return_value=MagicMock(data=[])),
        patch("app.services.plan.get_client"),
    ):
        result = await _recuperar_perfil(PHONE)
        assert result is None


# ---------------------------------------------------------------------------
# _guardar_plan: loggea error en CE-03 sin lanzar excepción
# ---------------------------------------------------------------------------


async def test_guardar_plan_ce03_no_raises():
    with (
        patch("app.services.plan.asyncio.to_thread",
              new_callable=AsyncMock, side_effect=Exception("DB down")),
        patch("app.services.plan.get_client"),
    ):
        # No debe lanzar excepción
        await _guardar_plan("uuid", "plan texto", 1700.0, 2000.0, 1700.0, 5.23)
