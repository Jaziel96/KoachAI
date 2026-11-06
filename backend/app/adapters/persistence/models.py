"""Modelos SQLAlchemy — esquema inicial (US-002).

Fuente de verdad del modelo de datos: `docs/plan-maestro.md`, sección 14
("Base de datos detallada"). Este archivo traduce ese DDL (escrito en SQL
genérico) a SQLAlchemy 2.0 + Postgres, sin renombrar columnas ni cambiar
semántica, salvo las decisiones explícitamente aprobadas para US-002:

- PK UUID con `gen_random_uuid()` (pgcrypto, ya activo en Supabase) en vez de
  `uuid_generate_v4()` (uuid-ossp).
- Timestamps como `TIMESTAMPTZ` (with time zone) en vez de `TIMESTAMP`.

Alcance de este archivo: únicamente las 6 tablas que pide US-002 (`users`,
`perfiles`, `configuracion_agente`, `consentimientos`, `conversacion_estado`,
`historial_conversacion`). El resto del esquema de la sección 14 (30+ tablas)
se agrega tabla por tabla en las US que las activan — no se adelanta aquí.

RLS: activado en todas las tablas con `user_id` (ver migración). Las políticas
usan `current_setting('app.current_user_id', true)::uuid` — ver
`app/adapters/persistence/db.py` para cómo se fija esa variable por transacción.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy import Enum as PgEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func, text

TZ = DateTime(timezone=True)


class Base(DeclarativeBase):
    """Base declarativa de todos los modelos ORM de Koach."""


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )


# ============================================
# USUARIOS
# ============================================


class User(Base):
    """Cuenta de usuario — identificada primero por teléfono de WhatsApp."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = _uuid_pk()
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(TZ, server_default=func.now(), nullable=False)
    plan_tier: Mapped[str] = mapped_column(
        PgEnum("free", "esencial", "coach", "coach_plus", "familia", name="plan_tier"),
        server_default="free",
        nullable=False,
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(TZ)
    status: Mapped[str] = mapped_column(
        PgEnum("active", "paused", "cancelled", "trial", "inactive", name="user_status"),
        server_default="trial",
        nullable=False,
    )
    mayor_edad_confirmado: Mapped[bool] = mapped_column(Boolean, server_default="false")
    canal_preferido: Mapped[str] = mapped_column(
        PgEnum("whatsapp", "app", "ambos", name="canal_preferido"),
        server_default="whatsapp",
        nullable=False,
    )
    es_founder: Mapped[bool] = mapped_column(Boolean, server_default="false")
    referido_por_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    ip_registro: Mapped[str | None] = mapped_column(String(45))
    user_agent_registro: Mapped[str | None] = mapped_column(Text)


class Perfil(Base):
    """Perfil físico y de metas del usuario. Relación 1:1 con `users`."""

    __tablename__ = "perfiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    nombre: Mapped[str | None] = mapped_column(String(100))
    genero: Mapped[str | None] = mapped_column(
        PgEnum("masculino", "femenino", "otro", "prefiero_no_decir", name="genero")
    )
    edad: Mapped[int | None] = mapped_column(Integer)
    peso_kg: Mapped[float | None]
    peso_inicial_kg: Mapped[float | None]
    talla_cm: Mapped[int | None] = mapped_column(Integer)
    meta: Mapped[str | None] = mapped_column(
        PgEnum(
            "bajar_peso",
            "ganar_musculo",
            "comer_mejor",
            "mas_energia",
            "mantener",
            name="meta_usuario",
        )
    )
    meta_peso_kg: Mapped[float | None]
    restricciones_alimentarias: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    alergias: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    condiciones_medicas: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    lesiones_previas: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    parq_completado: Mapped[bool] = mapped_column(Boolean, server_default="false")
    parq_aprobado: Mapped[bool] = mapped_column(Boolean, server_default="false")
    parq_pendiente_medico: Mapped[bool] = mapped_column(Boolean, server_default="false")
    motivacion_personal: Mapped[str | None] = mapped_column(Text)
    tono: Mapped[str] = mapped_column(
        PgEnum("drill", "coach", "amigo", "formal", name="tono_agente"),
        server_default="coach",
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(
        String(50), server_default="America/Mexico_City", nullable=False
    )
    ciclo_menstrual_activo: Mapped[bool] = mapped_column(Boolean, server_default="false")
    medicamentos_actuales: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    updated_at: Mapped[datetime] = mapped_column(TZ, server_default=func.now(), nullable=False)


class ConfiguracionAgente(Base):
    """Preferencias de horarios y notificaciones del agente. Relación 1:1 con `users`."""

    __tablename__ = "configuracion_agente"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    horarios: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    modo_silencio_hasta: Mapped[datetime | None] = mapped_column(TZ)
    frecuencia_peso: Mapped[str] = mapped_column(
        PgEnum("semanal", "quincenal", "mensual", name="frecuencia_peso"),
        server_default="semanal",
        nullable=False,
    )
    medidas_corporales_activas: Mapped[bool] = mapped_column(Boolean, server_default="false")
    fotos_progreso_activas: Mapped[bool] = mapped_column(Boolean, server_default="false")
    notificaciones_push_app: Mapped[bool] = mapped_column(Boolean, server_default="true")
    notificaciones_whatsapp: Mapped[bool] = mapped_column(Boolean, server_default="true")
    frecuencia_motivacional: Mapped[str] = mapped_column(
        PgEnum("baja", "media", "alta", name="frecuencia_motivacional"),
        server_default="media",
        nullable=False,
    )
    recordatorios_medicamentos: Mapped[bool] = mapped_column(Boolean, server_default="false")
    recordatorio_dormir: Mapped[bool] = mapped_column(Boolean, server_default="true")
    contacto_emergencia_nombre: Mapped[str | None] = mapped_column(String(100))
    contacto_emergencia_telefono: Mapped[str | None] = mapped_column(String(20))
    updated_at: Mapped[datetime] = mapped_column(TZ, server_default=func.now(), nullable=False)


# ============================================
# CONVERSACIÓN Y MEMORIA
# ============================================


class ConversacionEstado(Base):
    """Máquina de estados de flujos multi-paso (onboarding, etc.) — US-020."""

    __tablename__ = "conversacion_estado"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    flujo: Mapped[str | None] = mapped_column(String(50))
    paso_actual: Mapped[str | None] = mapped_column(String(50))
    contexto: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    intentos: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    ultima_interaccion: Mapped[datetime | None] = mapped_column(TZ)
    expira_at: Mapped[datetime | None] = mapped_column(TZ)


class HistorialConversacion(Base):
    """Cada turno (usuario o asistente) — auditoría y contexto para el agente.

    Nota (ADR-007): `tool_calls_log` y `acciones_pendientes` se agregan más
    adelante con el núcleo agéntico (US-159) — no forman parte de US-002.
    """

    __tablename__ = "historial_conversacion"
    __table_args__ = (
        Index("idx_historial_user_fecha", "user_id", "fecha"),
        Index(
            "uq_historial_message_id_externo",
            "message_id_externo",
            unique=True,
            postgresql_where=text("message_id_externo IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    fecha: Mapped[datetime | None] = mapped_column(TZ)
    role: Mapped[str | None] = mapped_column(PgEnum("user", "assistant", name="mensaje_role"))
    content: Mapped[str | None] = mapped_column(Text)
    canal: Mapped[str | None] = mapped_column(PgEnum("whatsapp", "app", name="canal"))
    tipo_mensaje: Mapped[str | None] = mapped_column(
        PgEnum(
            "proactivo",
            "respuesta_usuario",
            "registro",
            "consulta",
            "sistema",
            name="tipo_mensaje",
        )
    )
    tokens_used: Mapped[int | None] = mapped_column(Integer)
    modelo_usado: Mapped[str | None] = mapped_column(String(50))
    template_id: Mapped[str | None] = mapped_column(String(50))
    audio_url: Mapped[str | None] = mapped_column(String)
    audio_transcripcion: Mapped[str | None] = mapped_column(Text)
    # Id del mensaje asignado por el canal (p. ej. `wamid.*` de Meta) — US-017 CA-3.
    message_id_externo: Mapped[str | None] = mapped_column(String(100))


# ============================================
# LEGAL Y COMPLIANCE
# ============================================


class Consentimiento(Base):
    """Registro de consentimiento expreso (LFPDPPP) — US-021."""

    __tablename__ = "consentimientos"

    id: Mapped[uuid.UUID] = _uuid_pk()
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    tipo: Mapped[str | None] = mapped_column(
        PgEnum(
            "terminos",
            "privacidad",
            "datos_salud",
            "comunicaciones",
            "whatsapp_channel",
            name="tipo_consentimiento",
        )
    )
    aceptado: Mapped[bool | None] = mapped_column(Boolean)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(Text)
    version_documento: Mapped[str | None] = mapped_column(String(20))
    fecha: Mapped[datetime] = mapped_column(TZ, server_default=func.now(), nullable=False)
