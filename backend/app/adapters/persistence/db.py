"""Engine y sesiones async de SQLAlchemy, con soporte para RLS por usuario.

Los usuarios de Koach no se autentican vía Supabase Auth (no hay JWT en Fase 1 —
el canal principal es WhatsApp), así que las políticas RLS no pueden apoyarse en
`auth.uid()`. En su lugar, cada sesión de negocio corre dentro de una transacción
que fija una variable de configuración local de Postgres

    SET LOCAL app.current_user_id = '<uuid-del-usuario>'

y las políticas RLS (ver migración inicial) filtran con
`current_setting('app.current_user_id', true)::uuid`. `SET LOCAL` solo dura la
transacción activa, así que no hay fuga de contexto entre requests que reutilizan
la misma conexión del pool.

Nota: el backend usa por defecto una conexión con permisos de aplicación (no el
`service_role` de Supabase, que bypassa RLS por completo) — ver `SUPABASE_SERVICE_KEY`
en `app/core/config.py`, reservado para operaciones administrativas explícitas.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


def get_engine() -> AsyncEngine:
    """Crea el engine async a partir de DATABASE_URL."""
    settings = get_settings()
    return create_async_engine(str(settings.DATABASE_URL), pool_pre_ping=True)


_engine: AsyncEngine = get_engine()
_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=_engine, expire_on_commit=False
)


@asynccontextmanager
async def get_session(user_id: str | None = None) -> AsyncGenerator[AsyncSession]:
    """Abre una sesión y, si se da `user_id`, fija el contexto RLS de la transacción.

    Args:
        user_id: UUID del usuario dueño de los datos que se van a leer/escribir.
            Si es None, la sesión no tiene contexto RLS (solo para operaciones
            que no dependen de `user_id`, p. ej. lectura de tablas de catálogo).
    """
    async with _session_factory() as session, session.begin():
        if user_id is not None:
            await session.execute(
                text("SELECT set_config('app.current_user_id', :user_id, true)"),
                {"user_id": user_id},
            )
        yield session
