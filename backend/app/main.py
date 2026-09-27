"""Punto de entrada de la aplicación FastAPI (US-003)."""

import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.exceptions import unhandled_exception_handler
from app.core.logging import configure_logging, get_logger
from app.core.sentry import init_sentry

configure_logging()
logger = get_logger(__name__)

settings = get_settings()
init_sentry(settings)

app = FastAPI(title="Koach", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Asigna un `request_id` por petición y lo agrega al contexto de logging."""
    request_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(health_router)
