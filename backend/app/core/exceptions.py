"""Manejo global de excepciones no controladas (RF-4 / CA-4 de US-003).

Cualquier excepción que no haya sido capturada por un handler más específico
se registra completa en el log (para diagnóstico interno) pero al cliente se
le responde un 500 genérico, sin exponer el stack trace ni el mensaje interno.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Captura cualquier excepción no manejada y responde 500 sin filtrar detalles."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocurrió un error interno. Ya fue registrado."},
    )
