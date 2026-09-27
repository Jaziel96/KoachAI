"""Provider ficticio mínimo para CA-2: implementa las 3 interfaces completas."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.ai.providers.base_provider import (
    CompletionRequest,
    CompletionResponse,
    LLMProvider,
    ModelTier,
    StopReason,
    ToolCall,
    ToolResult,
    TranscriptionProvider,
    VisionProvider,
)


class MockLLMProvider(LLMProvider, TranscriptionProvider, VisionProvider):
    """Implementación mínima usada solo para verificar el contrato de la interface."""

    def __init__(self, supports_tools: bool = True) -> None:
        self._supports_tools = supports_tools

    @property
    def name(self) -> str:
        return "mock"

    @property
    def supported_tiers(self) -> list[ModelTier]:
        return [ModelTier.FAST, ModelTier.SMART, ModelTier.VISION, ModelTier.AUDIO]

    @property
    def supports_tools(self) -> bool:
        return self._supports_tools

    async def complete(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        self._reject_tools_if_unsupported(request)
        return CompletionResponse(
            content="respuesta mock",
            tokens_input=1,
            tokens_output=1,
            model_used="mock-model",
            provider=self.name,
            latency_ms=1,
        )

    async def stream(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> AsyncIterator[str]:
        self._reject_tools_if_unsupported(request)
        yield "respuesta mock"

    async def continue_with_tool_results(
        self,
        original_request: CompletionRequest,
        tool_calls: list[ToolCall],
        tool_results: list[ToolResult],
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        return CompletionResponse(
            content="respuesta final mock",
            tokens_input=1,
            tokens_output=1,
            model_used="mock-model",
            provider=self.name,
            latency_ms=1,
            stop_reason=StopReason.END_TURN,
        )

    async def health_check(self) -> bool:
        return True

    async def transcribe(self, audio_bytes: bytes, language: str = "es") -> str:
        return "transcripción mock"

    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        return "análisis mock"
