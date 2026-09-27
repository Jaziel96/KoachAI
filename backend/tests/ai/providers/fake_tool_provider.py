"""Provider ficticio para verificar el contrato de tool-use (CA-4 de US-006).

NOTA DE PROCESO (decisión explícita del usuario, ver plan aprobado de US-006):
`AnthropicProvider` es US-007 y todavía no existe. CA-4 pide verificar que un
`CompletionRequest` con `tools` no vacío, contra `AnthropicProvider`, retorne
`tool_calls`. Como ese provider real no existe aún, este `FakeToolProvider`
verifica el CONTRATO de la interface (que `LLMProvider.complete()` puede
retornar `stop_reason=TOOL_USE` con `tool_calls` pobladas cuando el request
trae `tools`) de forma determinista, sin llamar a ningún SDK real. Esta
verificación se debe REPETIR contra `AnthropicProvider` de verdad en US-007,
donde CA-4 se vuelve a marcar con el proveedor real — no se da por cerrada
la garantía end-to-end aquí.
"""

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
)


class FakeToolProvider(LLMProvider):
    """Simula, de forma determinista, que el modelo decide invocar una tool."""

    @property
    def name(self) -> str:
        return "fake-tool-provider"

    @property
    def supported_tiers(self) -> list[ModelTier]:
        return [ModelTier.SMART]

    @property
    def supports_tools(self) -> bool:
        return True

    async def complete(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        self._reject_tools_if_unsupported(request)
        if request.tools:
            primera_tool = request.tools[0]
            return CompletionResponse(
                content="",
                tokens_input=10,
                tokens_output=5,
                model_used="fake-model",
                provider=self.name,
                latency_ms=1,
                tool_calls=[
                    ToolCall(
                        id="call_fake_1",
                        name=primera_tool.name,
                        arguments={},
                    )
                ],
                stop_reason=StopReason.TOOL_USE,
            )
        return CompletionResponse(
            content="respuesta sin tools",
            tokens_input=10,
            tokens_output=5,
            model_used="fake-model",
            provider=self.name,
            latency_ms=1,
        )

    async def stream(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> AsyncIterator[str]:
        self._reject_tools_if_unsupported(request)
        yield "respuesta sin tools"

    async def continue_with_tool_results(
        self,
        original_request: CompletionRequest,
        tool_calls: list[ToolCall],
        tool_results: list[ToolResult],
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        resumen = "; ".join(r.content for r in tool_results)
        return CompletionResponse(
            content=f"respuesta final considerando: {resumen}",
            tokens_input=10,
            tokens_output=5,
            model_used="fake-model",
            provider=self.name,
            latency_ms=1,
            stop_reason=StopReason.END_TURN,
        )

    async def health_check(self) -> bool:
        return True


class FakeNoToolsProvider(LLMProvider):
    """Provider con `supports_tools = False`, para verificar CA-5."""

    @property
    def name(self) -> str:
        return "fake-no-tools-provider"

    @property
    def supported_tiers(self) -> list[ModelTier]:
        return [ModelTier.FAST]

    @property
    def supports_tools(self) -> bool:
        return False

    async def complete(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        self._reject_tools_if_unsupported(request)
        return CompletionResponse(
            content="respuesta sin soporte de tools",
            tokens_input=1,
            tokens_output=1,
            model_used="fake-model",
            provider=self.name,
            latency_ms=1,
        )

    async def stream(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> AsyncIterator[str]:
        self._reject_tools_if_unsupported(request)
        yield "respuesta sin soporte de tools"

    async def continue_with_tool_results(
        self,
        original_request: CompletionRequest,
        tool_calls: list[ToolCall],
        tool_results: list[ToolResult],
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        raise NotImplementedError("Este provider no soporta tools")

    async def health_check(self) -> bool:
        return True
