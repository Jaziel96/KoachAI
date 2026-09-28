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


class UnsupportedTierError(AIProviderError):
    """Se pidió un `ModelTier` que este proveedor no atiende.

    Es un error de configuración o de programación, no de disponibilidad: el
    router NO debe tratarlo como caída del proveedor ni hacer fallback en
    silencio, porque eso escondería el bug.
    """


class InvalidResponseError(AIProviderError):
    """El proveedor respondió, pero el contenido no cumple lo pedido.

    Por ejemplo, JSON inválido en `json_mode`. Nunca se devuelve basura como si
    fuera una respuesta válida.
    """
