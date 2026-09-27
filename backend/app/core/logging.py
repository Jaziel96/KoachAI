"""Configuración de logging estructurado (JSON) vía structlog.

Todo log de la aplicación pasa por `structlog` para poder correlacionar
eventos con `request_id` (ver middleware en `app/main.py`) — requerido por
RF-3/CA-3 de US-003.
"""

import logging
import sys

import structlog


def configure_logging(*, json_logs: bool = True) -> None:
    """Configura `structlog` y el logging estándar de Python para emitir JSON."""
    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    renderer: structlog.typing.Processor = (
        structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[*shared_processors, structlog.processors.format_exc_info, renderer],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)


def get_logger(*args: str) -> structlog.stdlib.BoundLogger:
    """Atajo para `structlog.get_logger()` con tipado explícito."""
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(*args)
    return logger
