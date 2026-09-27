"""Excepciones de la capa de IA (RF-6 de US-006)."""


class AIProviderError(Exception):
    """Base de todas las excepciones de proveedores de IA."""


class ProviderUnavailableError(AIProviderError):
    """El proveedor no pudo atender el request (caído, timeout, error de red)."""


class RateLimitError(AIProviderError):
    """El proveedor rechazó el request por límite de tasa."""


class ContentFilterError(AIProviderError):
    """El proveedor bloqueó el contenido por su propio filtro de seguridad."""


class ToolsNotSupportedError(AIProviderError):
    """El request incluye `tools` pero el proveedor declara `supports_tools = False` (RNF-3)."""
