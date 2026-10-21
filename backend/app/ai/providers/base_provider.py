"""Interface base de proveedores de IA, agnóstica de SDK (US-006, ADR-002, ADR-007).

Ningún import de aquí debe depender de un SDK de proveedor concreto
(anthropic, google.generativeai, openai, etc.) — CA-1 de US-006.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import StrEnum

from app.ai.exceptions import ToolsNotSupportedError


class ModelTier(StrEnum):
    """Nivel de capacidad requerido para una tarea."""

    FAST = "fast"
    SMART = "smart"
    VISION = "vision"
    AUDIO = "audio"


class StopReason(StrEnum):
    """Por qué el proveedor dejó de generar contenido (RF-11)."""

    END_TURN = "end_turn"
    TOOL_USE = "tool_use"
    MAX_TOKENS = "max_tokens"


@dataclass
class Message:
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class ToolDefinition:
    """Definición de una herramienta, en formato agnóstico de proveedor (RF-7)."""

    name: str
    description: str
    input_schema: dict[str, object]


@dataclass
class ToolCall:
    """Invocación de una tool decidida por el modelo (RF-9)."""

    id: str
    name: str
    arguments: dict[str, object]


@dataclass
class ToolResult:
    """Resultado de ejecutar una `ToolCall` contra la función de dominio (RF-9)."""

    tool_call_id: str
    content: str
    is_error: bool = False


@dataclass
class CompletionRequest:
    messages: list[Message]
    system_prompt: str | None = None
    max_tokens: int = 1024
    temperature: float = 0.7
    stop_sequences: list[str] | None = None
    json_mode: bool = False
    tools: list[ToolDefinition] | None = None


@dataclass
class CompletionResponse:
    content: str
    tokens_input: int
    tokens_output: int
    model_used: str
    provider: str
    latency_ms: int
    cost_usd: float | None = None
    tool_calls: list[ToolCall] | None = None
    stop_reason: StopReason = StopReason.END_TURN


class LLMProvider(ABC):
    """Interface que TODOS los proveedores de razonamiento deben implementar.

    Permite intercambiar Claude API ↔ Ollama local sin tocar lógica de negocio
    (ADR-002), y da soporte de tool-use nativo para el loop agéntico (ADR-007).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Identificador del proveedor."""
        ...

    @property
    @abstractmethod
    def supported_tiers(self) -> list[ModelTier]:
        """Qué tiers puede atender este proveedor."""
        ...

    @property
    @abstractmethod
    def supports_tools(self) -> bool:
        """Si este proveedor soporta tool-use nativo (RNF-3).

        Debe declararse explícitamente — no hay default `True` implícito.
        Un provider con `supports_tools = False` debe rechazar, vía
        `_reject_tools_if_unsupported()`, cualquier request con `tools` no
        vacío en vez de ignorarlos silenciosamente (CA-5).
        """
        ...

    def _reject_tools_if_unsupported(self, request: CompletionRequest) -> None:
        """Helper común: valida CA-5 antes de llamar al SDK del proveedor.

        No es abstracto porque la validación es idéntica para todo proveedor;
        cada implementación concreta la invoca al inicio de `complete()` y de
        `continue_with_tool_results()`.
        """
        if request.tools and not self.supports_tools:
            raise ToolsNotSupportedError(
                f"El proveedor '{self.name}' no soporta tool-use "
                f"(supports_tools=False) pero el request incluye "
                f"{len(request.tools)} tool(s)."
            )

    @abstractmethod
    async def complete(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        """Genera una respuesta completa."""
        ...

    @abstractmethod
    async def stream(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> AsyncIterator[str]:
        """Genera respuesta en streaming."""
        if False:  # pragma: no cover — hace que el tipo inferido sea un async generator
            yield ""

    @abstractmethod
    async def continue_with_tool_results(
        self,
        original_request: CompletionRequest,
        tool_calls: list[ToolCall],
        tool_results: list[ToolResult],
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        """Reenvía resultados de tools ya ejecutadas para la respuesta final (RF-12).

        Forma estándar de continuar, dentro del mismo turno de conversación,
        una llamada que retornó `stop_reason=TOOL_USE`: el backend ejecutó
        cada `ToolCall` contra la función de dominio correspondiente y aquí
        reenvía los `ToolResult` para que el modelo redacte la respuesta
        final en lenguaje natural.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verifica que el proveedor esté disponible."""
        ...


class TranscriptionProvider(ABC):
    """Interface para transcripción de audio."""

    @abstractmethod
    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "es",
    ) -> str: ...


class VisionProvider(ABC):
    """Interface para análisis de imágenes."""

    @abstractmethod
    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str,
    ) -> str: ...
