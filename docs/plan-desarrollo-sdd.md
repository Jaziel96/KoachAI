# KOACH — Plan de Desarrollo SDD
### Especificaciones, User Stories y Arquitectura Técnica
> Documento de ejecución técnica para desarrollo con Claude Code
> Versión 1.1 — Septiembre 2026 (agrega ADR-007: arquitectura agéntica con tool-use nativo, extiende US-006/US-009, reduce alcance de US-031, agrega US-159 y US-160)

---

## ÍNDICE

**Parte I — Fundamentos Técnicos**
1. Stack tecnológico definitivo
2. Decisiones arquitectónicas (ADRs)
3. Capa de abstracción de IA (crítica)
4. Estructura del proyecto
5. Convenciones de desarrollo

**Parte II — Metodología SDD**
6. Flujo de trabajo con Claude Code
7. Formato de specs y US
8. Definition of Done

**Parte III — Roadmap de Épicas**
9. Mapa completo de épicas
10. Dependencias entre épicas

**Parte IV — User Stories Detalladas**
11. FASE 0 — Fundación
12. FASE 1 — MVP WhatsApp
13. FASE 2 — Nutrición completa
14. FASE 3 — App y Dashboard
15. FASE 4 — Chat nativo y monetización
16. FASE 5 — Perfiles especializados

---

# PARTE I — FUNDAMENTOS TÉCNICOS

## 1. STACK TECNOLÓGICO DEFINITIVO

### 1.1 Backend

| Componente | Tecnología | Versión | Justificación |
|------------|-----------|---------|---------------|
| Lenguaje | Python | 3.11+ | Ecosistema IA, async nativo |
| Framework API | FastAPI | 0.110+ | Async, tipado, docs automáticas |
| Validación | Pydantic | v2 | Type safety, serialización |
| ORM | SQLAlchemy | 2.0+ | Async support, maduro |
| Migraciones | Alembic | 1.13+ | Versionado de esquema |
| Cola de tareas | Celery | 5.3+ | Mensajes programados |
| Broker/Cache | Redis | 7+ | Celery + caché de respuestas |
| Testing | pytest + pytest-asyncio | - | Estándar Python |
| Linting | ruff | - | Rápido, reemplaza flake8+black |
| Type checking | mypy | - | Detección temprana de errores |

### 1.2 Base de datos

| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| DB principal | PostgreSQL 15 (Supabase) | Relacional + JSONB + pgvector |
| Vectores | pgvector | Memoria semántica del agente (futuro) |
| Storage | Supabase Storage | Fotos, PDFs |
| Auth | Supabase Auth | Login app (Fase 3) |

### 1.3 Inteligencia Artificial

| Capa | Tecnología inicial | Migración futura |
|------|-------------------|------------------|
| Razonamiento | Claude API (Anthropic) | Llama 3.x / Qwen local |
| Clasificación rápida | Gemini 1.5 Flash | Phi-3 / Llama 3.2 local |
| Transcripción audio | Whisper API (OpenAI) | Whisper local (faster-whisper) |
| Visión | Claude Vision | LLaVA / Qwen-VL local |
| Embeddings | OpenAI text-embedding-3 | nomic-embed local |

**⚠️ CRÍTICO:** Todo acceso a IA pasa por la capa de abstracción (Sección 3). Nunca llamar APIs directamente desde lógica de negocio.

### 1.4 Frontend

| Componente | Tecnología | Fase |
|------------|-----------|------|
| Landing web | Next.js 14 + TypeScript + Tailwind | Fase 0 |
| Dashboard web | Next.js (mismo proyecto) | Fase 3 |
| App móvil | React Native + Expo | Fase 3 |
| UI components | shadcn/ui | Fase 0 |
| Estado | Zustand | Fase 3 |
| Charts | Recharts | Fase 3 |

### 1.5 Infraestructura

| Servicio | Proveedor | Costo inicial |
|----------|-----------|---------------|
| Backend hosting | Railway | $5-10 USD/mes |
| Frontend hosting | Vercel | $0 (free tier) |
| Base de datos | Supabase | $0 → $25 USD/mes |
| Redis | Railway addon | Incluido |
| Observabilidad | Sentry | $0 (free tier) |
| Analytics | PostHog | $0 (free tier) |
| Emails | Resend | $0 (3k/mes) |

### 1.6 Integraciones externas

| Servicio | Uso | Fase |
|----------|-----|------|
| WhatsApp Cloud API | Canal principal | Fase 1 |
| Conekta | Pagos MXN | Fase 4 |
| Facturama | CFDI automático | Fase 4 |
| Google Places API | Gyms cercanos | Fase 2 |
| Google Calendar API | Agenda (opcional) | Fase 4 |

---

## 2. DECISIONES ARQUITECTÓNICAS (ADRs)

Estas decisiones se documentan en `/docs/decisions/` como Architecture Decision Records.

### ADR-001: Arquitectura hexagonal (Ports & Adapters)

**Contexto:** Necesitamos poder cambiar proveedores de IA, canales de mensajería y almacenamiento sin reescribir lógica de negocio.

**Decisión:** Arquitectura hexagonal con:
- **Domain** — lógica pura de negocio, sin dependencias externas
- **Ports** — interfaces abstractas
- **Adapters** — implementaciones concretas (Claude, WhatsApp, Supabase)

**Consecuencias:**
- ✅ Migrar a IA local no requiere tocar lógica de negocio
- ✅ Testeable sin llamadas reales a APIs
- ✅ Podemos agregar Telegram/SMS sin refactor
- ⚠️ Más archivos y abstracción inicial

---

### ADR-002: Capa de abstracción de IA agnóstica de proveedor

**Contexto:** Iniciamos con APIs (Claude, Gemini, Whisper) pero queremos migrar a modelos locales para reducir costos y ganar privacidad.

**Decisión:** Interface `LLMProvider` con implementaciones intercambiables vía configuración.

**Consecuencias:**
- ✅ Cambio de proveedor = cambio de variable de entorno
- ✅ Podemos correr híbrido (algunas tareas local, otras API)
- ✅ Testing con mock provider
- ⚠️ No podemos usar features exclusivas de un proveedor sin abstraerlas

---

### ADR-003: Prompts como recursos versionados

**Contexto:** Los prompts son el "código" del comportamiento del agente. Deben versionarse, testearse y poder cambiar sin deploy.

**Decisión:** Prompts en archivos YAML/Jinja2 separados del código, cargados en runtime.

**Estructura:**
```
app/ai/prompts/
├── system/
│   ├── koach_base.yaml
│   ├── perfil_diabetes.yaml
│   └── perfil_postparto.yaml
├── tasks/
│   ├── onboarding.yaml
│   ├── registro_comida.yaml
│   └── generar_plan.yaml
└── templates/
    └── whatsapp_messages.yaml
```

**Consecuencias:**
- ✅ Iterar prompts sin redeploy
- ✅ A/B testing de prompts
- ✅ Prompts por perfil de usuario
- ✅ Versionado en git

---

### ADR-004: Estado conversacional en base de datos, no en memoria

**Contexto:** El onboarding y flujos multi-paso requieren estado. Celery workers son stateless.

**Decisión:** Máquina de estados persistida en tabla `conversacion_estado`.

**Consecuencias:**
- ✅ Escalable horizontalmente
- ✅ Resiliente a reinicios
- ✅ Auditable
- ⚠️ Una query extra por mensaje

---

### ADR-005: Router de IA por costo y capacidad

**Contexto:** No todas las tareas requieren el modelo más caro.

**Decisión:** Router que clasifica la tarea y elige el modelo apropiado.

**Niveles:**
1. **Template** (costo $0) — mensajes fijos
2. **Fast** (Gemini Flash / Llama 3.2 local) — clasificación, extracción simple
3. **Smart** (Claude Sonnet / Llama 70B local) — razonamiento, empatía, planes
4. **Vision** (Claude Vision / LLaVA local) — análisis de imágenes

---

### ADR-006: Multi-tenancy por usuario con RLS

**Contexto:** Datos de salud sensibles, múltiples usuarios.

**Decisión:** Row Level Security de PostgreSQL activo en todas las tablas.

---

### ADR-007: Arquitectura agéntica con tool-use nativo (reemplaza clasificar-y-rutear)

**Contexto:** El diseño original (US-031) usaba un clasificador de intención en tier FAST (Gemini) que determinaba una categoría (`registro_comida`, `registro_ejercicio`, etc.) y el backend rutea manualmente al handler correspondiente, invocando a Claude solo para las tareas que requerían razonamiento. Esto funciona, pero tiene tres limitantes: (1) un mensaje que mezcla varias intenciones ("ya comí, y también quiero pausar los recordatorios de la tarde") requiere lógica ad-hoc para dividirlo; (2) agregar una nueva capacidad implica tocar el clasificador Y el router Y el handler; (3) no aprovecha que Claude ya soporta *tool use* nativo — dado un mensaje, contexto del usuario y una lista de herramientas disponibles, el propio modelo decide cuáles invocar (una o varias) sin que el backend tenga que adivinar la intención de antemano.

**Decisión:** Koach se rediseña como un agente con tool-use nativo de Anthropic:

1. Cada turno de conversación, Claude (tier SMART) recibe: el mensaje del usuario, su contexto relevante (perfil, estado, historial reciente), el system prompt, y la lista de herramientas (`tools`) disponibles según su estado de cuenta y fase del producto habilitada.
2. Claude decide si responde directamente (texto) o invoca una o más herramientas (`tool_calls`) — por ejemplo, un solo mensaje puede disparar `registrar_comida` y `ajustar_horario_mensajes` en el mismo turno.
3. El backend ejecuta cada tool call contra la función de dominio/servicio correspondiente (nunca contra la IA otra vez para "confirmar" — la función es determinista) y devuelve el resultado a Claude para que redacte la respuesta final al usuario.
4. El clasificador de intención (US-031) **no se elimina, se reduce de alcance**: pasa de ser el router principal a una capa barata de pre-filtro para dos casos donde SÍ conviene decidir antes de gastar una llamada a tier SMART: (a) comandos exactos ("AYUDA", "PAUSA", "BORRAR MIS DATOS") que no necesitan razonamiento, y (b) pre-screening de crisis (US-032), que sigue teniendo prioridad absoluta y corre ANTES de entrar al loop agéntico, nunca como una tool más entre otras.

**Principios de seguridad no negociables para el diseño de herramientas (aplican a toda US-159 en adelante):**
- **Defense in depth, no confianza ciega en el modelo:** cada tool que registra datos de salud o cambia estado del usuario valida sus propios límites en código determinista (p. ej. `registrar_peso` rechaza deltas > 15% sin confirmación, sin importar qué decida el modelo). El modelo elige *qué* tool llamar; la función decide *si el resultado es seguro* de aplicar.
- **Los límites de seguridad viven en las funciones, no en el prompt.** Un prompt puede ignorarse (prompt injection, alucinación); una validación en `app/domain/` no.
- **Crisis y derivación profesional nunca son "una tool más".** `marcar_crisis` y `derivar_a_profesional` se pueden invocar desde el loop agéntico, pero la detección de crisis (US-032) sigue corriendo como guard previo e independiente — si detecta crisis, el loop agéntico ni se ejecuta ese turno.
- **Toda tool call se registra** en `historial_conversacion` (qué tool, qué argumentos, qué resultado) para auditoría — es un requisito de las brechas de seguridad ya identificadas (prompt injection, ver `koach-analisis-brechas.md` sección 2.2).

**Consecuencias:**
- ✅ Un mensaje puede resolver varias intenciones en un solo turno, de forma natural
- ✅ Agregar una capacidad nueva = agregar una tool + su función de dominio, sin tocar un router central
- ✅ El modelo maneja mejor la ambigüedad conversacional que un clasificador rígido de categorías
- ✅ Se alinea con hacia dónde va el ecosistema de Anthropic (tool use es de primera clase, no un parche)
- ⚠️ Más tokens por turno (se envía la lista de tools disponibles) — mitigado limitando qué tools se exponen según fase/estado del usuario
- ⚠️ Requiere que `LLMProvider` y `AIRouter` soporten `tools`/`tool_calls` (ver extensión de US-006 y US-009 abajo)
- ⚠️ Requiere más disciplina de testing: cada tool necesita tests de "qué pasa si el modelo la llama con argumentos raros o fuera de contexto"

---

## 3. CAPA DE ABSTRACCIÓN DE IA (CRÍTICA)

Esta es la decisión más importante para tu migración futura a local.

### 3.1 Estructura

```
app/ai/
├── __init__.py
├── base.py                    # Interfaces abstractas
├── router.py                  # Selección de provider por tarea
├── config.py                  # Configuración de providers
├── exceptions.py              # Errores específicos de IA
│
├── providers/
│   ├── __init__.py
│   ├── base_provider.py       # Clase abstracta LLMProvider
│   ├── anthropic_provider.py  # Claude API
│   ├── gemini_provider.py     # Gemini API
│   ├── openai_provider.py     # Whisper, embeddings
│   ├── ollama_provider.py     # 🔮 Futuro: modelos locales
│   ├── vllm_provider.py       # 🔮 Futuro: vLLM server
│   └── mock_provider.py       # Testing
│
├── prompts/
│   ├── loader.py              # Carga y renderiza prompts
│   ├── system/
│   ├── tasks/
│   └── templates/
│
└── tasks/                     # Tareas de alto nivel
    ├── __init__.py
    ├── onboarding.py
    ├── meal_parsing.py
    ├── plan_generation.py
    ├── exercise_guidance.py
    └── crisis_detection.py
```

### 3.2 Interface base

```python
# app/ai/providers/base_provider.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import AsyncIterator


class ModelTier(str, Enum):
    """Nivel de capacidad requerido para una tarea."""
    FAST = "fast"        # Clasificación, extracción simple
    SMART = "smart"      # Razonamiento, empatía, generación
    VISION = "vision"    # Análisis de imágenes
    AUDIO = "audio"      # Transcripción


@dataclass
class Message:
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class CompletionRequest:
    messages: list[Message]
    system_prompt: str | None = None
    max_tokens: int = 1024
    temperature: float = 0.7
    stop_sequences: list[str] | None = None
    json_mode: bool = False


@dataclass
class CompletionResponse:
    content: str
    tokens_input: int
    tokens_output: int
    model_used: str
    provider: str
    latency_ms: int
    cost_usd: float | None = None


class LLMProvider(ABC):
    """
    Interface que TODOS los proveedores deben implementar.
    Permite intercambiar Claude API ↔ Ollama local sin tocar lógica de negocio.
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
    ) -> str:
        ...


class VisionProvider(ABC):
    """Interface para análisis de imágenes."""

    @abstractmethod
    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str,
    ) -> str:
        ...
```

### 3.3 Router de IA

```python
# app/ai/router.py

class AIRouter:
    """
    Decide qué proveedor usar según:
    - Tier requerido por la tarea
    - Disponibilidad del proveedor
    - Configuración (local vs API)
    - Costo objetivo
    """

    def __init__(self, config: AIConfig):
        self.providers: dict[str, LLMProvider] = {}
        self.config = config
        self._register_providers()

    def _register_providers(self) -> None:
        """Registra proveedores según configuración."""
        # En Fase 1: Anthropic + Gemini
        # En futuro: agregar Ollama sin cambiar nada más
        ...

    async def complete(
        self,
        request: CompletionRequest,
        tier: ModelTier,
        prefer_local: bool = False,
    ) -> CompletionResponse:
        """
        Rutea a proveedor apropiado con fallback.
        prefer_local permite forzar modelos locales cuando existan.
        """
        provider = self._select_provider(tier, prefer_local)
        try:
            return await provider.complete(request, tier)
        except ProviderUnavailableError:
            fallback = self._get_fallback(tier, exclude=provider.name)
            return await fallback.complete(request, tier)
```

### 3.4 Configuración por variables de entorno

```bash
# .env — Fase 1 (APIs)
AI_STRATEGY=api
AI_SMART_PROVIDER=anthropic
AI_FAST_PROVIDER=gemini
AI_AUDIO_PROVIDER=openai
AI_VISION_PROVIDER=anthropic

ANTHROPIC_API_KEY=sk-...
GEMINI_API_KEY=...
OPENAI_API_KEY=sk-...

# .env — Futuro (híbrido)
AI_STRATEGY=hybrid
AI_SMART_PROVIDER=anthropic      # Sigue en API para calidad
AI_FAST_PROVIDER=ollama          # Local para volumen
AI_AUDIO_PROVIDER=local_whisper  # Local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_FAST_MODEL=llama3.2:3b

# .env — Futuro (100% local)
AI_STRATEGY=local
AI_SMART_PROVIDER=vllm
VLLM_BASE_URL=http://gpu-server:8000
VLLM_MODEL=meta-llama/Llama-3.3-70B-Instruct
```

### 3.5 Uso desde lógica de negocio

```python
# app/services/meal_service.py
# ⚠️ NUNCA importa anthropic, gemini, ni ningún SDK directamente

from app.ai.tasks.meal_parsing import parse_meal_description

async def register_meal(user_id: UUID, text: str) -> MealRecord:
    # La lógica de negocio no sabe ni le importa qué modelo se usa
    parsed = await parse_meal_description(
        text=text,
        user_context=await get_user_context(user_id),
    )
    return await save_meal(user_id, parsed)
```

### 3.6 Checklist de migración futura a local

Cuando quieras migrar a local, solo necesitas:

- [ ] Implementar `OllamaProvider` o `VLLMProvider` heredando de `LLMProvider`
- [ ] Registrarlo en `AIRouter._register_providers()`
- [ ] Cambiar variables de entorno
- [ ] Ajustar prompts si el modelo local requiere formato distinto
- [ ] Correr suite de tests de regresión de prompts

**Cero cambios en lógica de negocio.**

---

## 4. ESTRUCTURA DEL PROYECTO

```
koach/
├── README.md
├── CLAUDE.md                      # Instrucciones para Claude Code
├── .gitignore
├── docker-compose.yml             # Redis local para dev
│
├── docs/
│   ├── plan-maestro.md
│   ├── plan-desarrollo-sdd.md     # Este documento
│   ├── decisions/                 # ADRs
│   │   ├── 001-arquitectura-hexagonal.md
│   │   ├── 002-abstraccion-ia.md
│   │   └── ...
│   └── specs/                     # Specs por US
│       ├── EP-00/
│       ├── EP-01/
│       └── ...
│
├── backend/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env.example
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app
│   │   │
│   │   ├── core/
│   │   │   ├── config.py          # Settings con Pydantic
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── domain/                # 🔷 Lógica pura de negocio
│   │   │   ├── entities/
│   │   │   │   ├── user.py
│   │   │   │   ├── meal.py
│   │   │   │   ├── workout.py
│   │   │   │   └── plan.py
│   │   │   ├── value_objects/
│   │   │   │   ├── macros.py
│   │   │   │   └── tdee.py
│   │   │   └── services/          # Reglas de negocio puras
│   │   │       ├── tdee_calculator.py
│   │   │       ├── macro_distributor.py
│   │   │       └── streak_calculator.py
│   │   │
│   │   ├── ports/                 # 🔌 Interfaces
│   │   │   ├── messaging.py       # MessagingChannel
│   │   │   ├── repositories.py    # UserRepository, etc.
│   │   │   └── storage.py         # FileStorage
│   │   │
│   │   ├── adapters/              # 🔧 Implementaciones
│   │   │   ├── messaging/
│   │   │   │   ├── whatsapp.py
│   │   │   │   └── websocket.py   # Fase 4
│   │   │   ├── persistence/
│   │   │   │   ├── models.py      # SQLAlchemy
│   │   │   │   └── repositories/
│   │   │   └── storage/
│   │   │       └── supabase_storage.py
│   │   │
│   │   ├── ai/                    # 🤖 Capa de IA (ver sección 3)
│   │   │
│   │   ├── services/              # 🎯 Orquestación
│   │   │   ├── onboarding_service.py
│   │   │   ├── meal_service.py
│   │   │   ├── workout_service.py
│   │   │   ├── plan_service.py
│   │   │   ├── proactive_service.py
│   │   │   └── report_service.py
│   │   │
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── webhooks.py    # WhatsApp
│   │   │       ├── users.py
│   │   │       ├── plans.py
│   │   │       └── admin.py
│   │   │
│   │   ├── workers/               # ⏰ Celery
│   │   │   ├── celery_app.py
│   │   │   ├── scheduled.py       # Mensajes proactivos
│   │   │   └── reports.py         # Generación PDFs
│   │   │
│   │   └── schemas/               # Pydantic DTOs
│   │       ├── whatsapp.py
│   │       ├── user.py
│   │       └── plan.py
│   │
│   ├── migrations/                # Alembic
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       ├── integration/
│       └── e2e/
│
├── frontend-web/                  # Next.js
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── public/
│
└── mobile/                        # React Native (Fase 3)
    └── ...
```

---

## 5. CONVENCIONES DE DESARROLLO

### 5.1 Git

**Branches:**
```
main                    # Producción
develop                 # Integración
feature/EP-01-US-003    # Features
fix/descripcion-corta   # Bugfixes
```

**Commits (Conventional Commits):**
```
feat(onboarding): agregar validación de edad mínima
fix(whatsapp): corregir parseo de mensajes de audio
docs(specs): agregar spec EP-02-US-005
refactor(ai): extraer router a módulo separado
test(meals): agregar tests de parseo de comidas mexicanas
chore(deps): actualizar FastAPI a 0.111
```

**Referencia a issues:**
```
feat(onboarding): completar flujo de 5 preguntas

Closes #12
```

### 5.2 Código

- **Type hints obligatorios** en todo el código Python
- **Docstrings** en funciones públicas (formato Google)
- **Máximo 50 líneas por función**
- **Máximo 300 líneas por archivo** (si excede, dividir)
- **Nombres en inglés** en código, **español** en prompts y mensajes al usuario

### 5.3 Testing

**Cobertura mínima por capa:**
- `domain/` → 90% (lógica pura, fácil de testear)
- `services/` → 70%
- `adapters/` → 50% (mocks)
- `api/` → 60%

**Estructura de test:**
```python
def test_calcular_tdee_hombre_sedentario():
    # Arrange
    perfil = Perfil(genero="M", edad=30, peso=80, talla=175)

    # Act
    tdee = calcular_tdee(perfil, nivel_actividad="sedentario")

    # Assert
    assert 2000 <= tdee <= 2200
```

### 5.4 CLAUDE.md (instrucciones para Claude Code)

Archivo en raíz del repo que Claude Code lee automáticamente:

```markdown
# Instrucciones para Claude Code — Proyecto Koach

## Contexto
Koach es un agente de salud proactivo por WhatsApp para mexicanos.
Lee `docs/plan-maestro.md` para contexto completo del producto.

## Reglas técnicas NO NEGOCIABLES

1. **NUNCA importar SDKs de IA directamente en lógica de negocio.**
   Todo acceso a IA pasa por `app/ai/`.

2. **NUNCA hardcodear prompts en código Python.**
   Los prompts van en `app/ai/prompts/` como YAML.

3. **NUNCA guardar secretos en código.**
   Usar `app/core/config.py` con Pydantic Settings.

4. **SIEMPRE type hints.** El proyecto usa mypy en strict mode.

5. **SIEMPRE RLS en tablas nuevas de Supabase.**

6. **Mensajes al usuario en español mexicano**, código en inglés.

## Antes de implementar
1. Lee la spec en `docs/specs/EP-XX/US-YYY.md`
2. Verifica dependencias con otras US
3. Propón plan de implementación antes de escribir código

## Comandos frecuentes
- Tests: `pytest -v`
- Lint: `ruff check . && mypy app`
- Migración: `alembic revision --autogenerate -m "descripcion"`
- Dev server: `uvicorn app.main:app --reload`
```

---

# PARTE II — METODOLOGÍA SDD

## 6. FLUJO DE TRABAJO CON CLAUDE CODE

### 6.1 Ciclo por User Story

```
1. SPEC      → Escribir spec detallada (con Claude en chat)
2. PLAN      → Claude Code propone plan de implementación
3. APPROVE   → Tú revisas y apruebas el plan
4. IMPLEMENT → Claude Code implementa paso a paso
5. TEST      → Correr tests, verificar criterios de aceptación
6. REVIEW    → Tú revisas el código
7. COMMIT    → Commit + PR + merge
8. CLOSE     → Cerrar issue en GitHub Projects
```

### 6.2 Comandos de Claude Code sugeridos

Crear en `.claude/commands/`:

**`/spec [US-ID]`** — Genera spec detallada para una US
**`/implement [US-ID]`** — Implementa según spec existente
**`/test [modulo]`** — Genera tests para un módulo
**`/review`** — Revisa cambios pendientes antes de commit
**`/adr [tema]`** — Documenta una decisión arquitectónica

### 6.3 Sesión típica de trabajo (1 hora)

```
[5 min]  Abrir Claude Code en el proyecto
         Leer spec de la US del día

[5 min]  /implement US-XXX
         Claude Code propone plan

[5 min]  Revisar plan, ajustar si necesario, aprobar

[30 min] Claude Code implementa
         Tú revisas incrementalmente

[10 min] Correr tests, verificar criterios de aceptación

[5 min]  Commit, push, cerrar issue
```

---

## 7. FORMATO DE SPECS Y US

### 7.1 Plantilla de User Story

```markdown
# US-XXX: [Título descriptivo]

**Épica:** EP-XX
**Fase:** X
**Estimación:** X horas
**Prioridad:** Alta / Media / Baja
**Estado:** Backlog / To Do / Doing / Review / Done

## Historia

**Como** [rol]
**Quiero** [funcionalidad]
**Para que** [beneficio]

## Contexto

[Por qué existe esta US, qué problema resuelve, relación con el plan maestro]

## Requisitos Funcionales

RF-1. El sistema debe...
RF-2. Cuando el usuario..., el sistema debe...
RF-3. Si ocurre..., el sistema debe...

## Requisitos No Funcionales

RNF-1. Tiempo de respuesta < X ms
RNF-2. Debe funcionar con proveedores de IA intercambiables
RNF-3. Todos los datos sensibles cifrados

## Modelo de datos

[Tablas afectadas, campos nuevos, migraciones necesarias]

## Contratos / Interfaces

[Signatures de funciones, schemas de API, formatos de mensaje]

## Flujos

### Flujo principal
1. ...
2. ...

### Flujos alternativos
- Si X entonces...

### Casos de error
- Error A → manejo

## Criterios de Aceptación

- [ ] CA-1: Dado [contexto], cuando [acción], entonces [resultado]
- [ ] CA-2: ...
- [ ] CA-3: ...

## Tests requeridos

- Unit: [qué probar]
- Integration: [qué probar]
- E2E: [escenario]

## Dependencias

- Requiere: US-XXX completada
- Bloquea: US-YYY

## Notas técnicas

[Decisiones, gotchas, referencias]

## Fuera de alcance

[Qué NO incluye esta US para evitar scope creep]
```

---

## 8. DEFINITION OF DONE

Una US está DONE cuando:

- [ ] Todos los criterios de aceptación se cumplen
- [ ] Tests unitarios pasan con cobertura mínima
- [ ] Tests de integración pasan (si aplica)
- [ ] `ruff check` y `mypy` sin errores
- [ ] Migración de DB aplicada y reversible
- [ ] Documentación actualizada (si cambia API pública)
- [ ] Probado manualmente en entorno local
- [ ] Deployed a producción sin errores
- [ ] Issue cerrado en GitHub Projects

---

# PARTE III — ROADMAP DE ÉPICAS

## 9. MAPA COMPLETO DE ÉPICAS

### FASE 0 — Fundación (Semanas 1-3, ~30 hrs)

| Épica | Nombre | US | Horas |
|-------|--------|-----|-------|
| EP-00 | Setup e infraestructura | 6 | 12 |
| EP-01 | Capa de abstracción IA | 5 | 12 (↑ soporte tool-use, ADR-007) |
| EP-02 | Landing web | 4 | 8 |

### FASE 1 — MVP WhatsApp (Semana 4 + 5-8, ~80 hrs)

| Épica | Nombre | US | Horas |
|-------|--------|-----|-------|
| EP-03 | Canal WhatsApp | 5 | 12 |
| EP-04 | Onboarding conversacional | 6 | 16 |
| EP-05 | Generación de planes | 5 | 14 |
| EP-06 | Registro de actividad | 6 | 15 (↓ US-031 reducida) |
| EP-06 bis | Núcleo agéntico (ADR-007) | 2 (US-159, US-160) | 10 |
| EP-07 | Motor de proactividad | 5 | 14 |
| EP-08 | Rachas y resúmenes | 3 | 8 |

### FASE 2 — Nutrición completa (Semanas 9-16, ~80 hrs)

| Épica | Nombre | US | Horas |
|-------|--------|-----|-------|
| EP-09 | Alacena inteligente | 4 | 12 |
| EP-10 | Plan semanal automático | 4 | 14 |
| EP-11 | Lista de compras | 3 | 8 |
| EP-12 | Modo "Comí Fuera" | 3 | 10 |
| EP-13 | Audio y voz | 3 | 10 |
| EP-14 | Biblioteca de ejercicios | 4 | 12 |
| EP-15 | Aprendizaje de patrones | 3 | 14 |

### FASE 3 — App y Dashboard (Semanas 17-24, ~80 hrs)

| Épica | Nombre | US | Horas |
|-------|--------|-----|-------|
| EP-16 | Dashboard web base | 5 | 18 |
| EP-17 | App móvil base | 6 | 24 |
| EP-18 | Reportes PDF | 4 | 14 |
| EP-19 | Modo gym avanzado | 4 | 12 |
| EP-20 | Notificaciones push | 3 | 12 |

### FASE 4 — Chat nativo y monetización (Semanas 25-32, ~80 hrs)

| Épica | Nombre | US | Horas |
|-------|--------|-----|-------|
| EP-21 | Chat nativo en app | 5 | 20 |
| EP-22 | Pagos y suscripciones | 6 | 22 |
| EP-23 | Facturación CFDI | 3 | 12 |
| EP-24 | Sistema de referidos | 3 | 10 |
| EP-25 | Analytics y métricas | 4 | 16 |

### FASE 5 — Perfiles especializados (Semanas 33+)

| Épica | Nombre | US | Horas |
|-------|--------|-----|-------|
| EP-26 | Sistema de perfiles | 4 | 16 |
| EP-27 | Perfil Post-parto | 4 | 14 |
| EP-28 | Perfil Adulto Mayor | 4 | 14 |
| EP-29 | Perfil Diabetes T2 | 5 | 20 |
| EP-30 | Migración a IA local | 5 | 24 |

---

## 10. DEPENDENCIAS ENTRE ÉPICAS

```
EP-00 (Setup)
  ├─→ EP-01 (Abstracción IA)
  │     ├─→ EP-04 (Onboarding)
  │     ├─→ EP-05 (Planes)
  │     └─→ EP-06 (Registro)
  │
  ├─→ EP-02 (Landing) [independiente]
  │
  └─→ EP-03 (WhatsApp)
        ├─→ EP-04 (Onboarding)
        └─→ EP-07 (Proactividad)
              └─→ EP-08 (Rachas)

EP-06 (Registro)
  └─→ EP-09 (Alacena)
        └─→ EP-10 (Plan semanal)
              └─→ EP-11 (Lista compras)

EP-01 (Abstracción IA)
  └─→ EP-13 (Audio) [necesita TranscriptionProvider]
  └─→ EP-30 (IA local) [implementa nuevos providers]

EP-16/17 (Dashboard/App)
  └─→ EP-21 (Chat nativo)
        └─→ EP-22 (Pagos)
```

---

# PARTE IV — USER STORIES DETALLADAS

---

# 11. FASE 0 — FUNDACIÓN

## EP-00 — Setup e Infraestructura

---

### US-000: Estructura base del repositorio

**Estimación:** 2 hrs | **Prioridad:** Crítica

**Como** desarrollador
**Quiero** una estructura de proyecto clara y estándar
**Para que** Claude Code y yo trabajemos con contexto consistente

**Requisitos Funcionales:**
- RF-1. Estructura de carpetas según ADR-001 (hexagonal)
- RF-2. `CLAUDE.md` con instrucciones para Claude Code
- RF-3. `.gitignore` completo (Python, Node, IDEs, secretos)
- RF-4. `README.md` con setup instructions
- RF-5. Carpeta `docs/` con plan maestro y specs

**Criterios de Aceptación:**
- [ ] CA-1: `git clone` + seguir README permite levantar el proyecto
- [ ] CA-2: `CLAUDE.md` existe y contiene reglas no negociables
- [ ] CA-3: Ningún secreto está commiteado (verificar con `git-secrets`)

**Fuera de alcance:** CI/CD, Docker de producción

---

### US-001: Configuración de entorno backend

**Estimación:** 2 hrs | **Prioridad:** Crítica

**Como** desarrollador
**Quiero** un entorno Python reproducible
**Para que** el desarrollo sea consistente entre local y producción

**Requisitos Funcionales:**
- RF-1. `pyproject.toml` con dependencias y herramientas
- RF-2. Configuración de `ruff`, `mypy`, `pytest`
- RF-3. `app/core/config.py` con Pydantic Settings
- RF-4. `.env.example` documentando todas las variables
- RF-5. `docker-compose.yml` con Redis para desarrollo local

**Contratos:**
```python
# app/core/config.py
class Settings(BaseSettings):
    # App
    APP_NAME: str = "Koach"
    ENVIRONMENT: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = False

    # Database
    DATABASE_URL: PostgresDsn
    SUPABASE_URL: HttpUrl
    SUPABASE_SERVICE_KEY: SecretStr

    # Redis
    REDIS_URL: RedisDsn

    # AI
    AI_STRATEGY: Literal["api", "hybrid", "local"] = "api"
    AI_SMART_PROVIDER: str = "anthropic"
    AI_FAST_PROVIDER: str = "gemini"
    ANTHROPIC_API_KEY: SecretStr | None = None
    GEMINI_API_KEY: SecretStr | None = None

    # WhatsApp
    WHATSAPP_TOKEN: SecretStr
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_VERIFY_TOKEN: SecretStr

    model_config = SettingsConfigDict(env_file=".env")
```

**Criterios de Aceptación:**
- [ ] CA-1: `pip install -e .` instala todas las dependencias
- [ ] CA-2: `ruff check .` pasa sin errores
- [ ] CA-3: `mypy app` pasa sin errores
- [ ] CA-4: Falta de variable requerida lanza error claro al arrancar
- [ ] CA-5: `docker-compose up` levanta Redis funcional

---

### US-002: Esquema inicial de base de datos

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** sistema
**Quiero** un esquema de base de datos versionado
**Para que** los cambios sean trazables y reversibles

**Requisitos Funcionales:**
- RF-1. Alembic configurado con Supabase
- RF-2. Migración inicial con tablas core:
  - `users`
  - `perfiles`
  - `configuracion_agente`
  - `consentimientos`
  - `conversacion_estado`
  - `historial_conversacion`
- RF-3. RLS activado en todas las tablas
- RF-4. Índices según plan maestro

**Modelo de datos:** Ver `docs/plan-maestro.md` sección 14.

**Criterios de Aceptación:**
- [ ] CA-1: `alembic upgrade head` crea todas las tablas
- [ ] CA-2: `alembic downgrade -1` revierte sin errores
- [ ] CA-3: RLS activo verificado con query de prueba
- [ ] CA-4: Un usuario no puede leer datos de otro usuario

---

### US-003: FastAPI base con health check

**Estimación:** 2 hrs | **Prioridad:** Crítica

**Como** operador
**Quiero** un endpoint de salud del sistema
**Para que** pueda monitorear el estado en producción

**Requisitos Funcionales:**
- RF-1. `GET /health` retorna estado de dependencias
- RF-2. Verifica: DB, Redis, proveedores de IA
- RF-3. Logging estructurado (JSON) configurado
- RF-4. Manejo global de excepciones
- RF-5. CORS configurado para dominio de la app

**Contratos:**
```python
# GET /health
{
  "status": "healthy" | "degraded" | "unhealthy",
  "version": "0.1.0",
  "checks": {
    "database": {"status": "up", "latency_ms": 12},
    "redis": {"status": "up", "latency_ms": 3},
    "ai_smart": {"status": "up", "provider": "anthropic"},
    "ai_fast": {"status": "up", "provider": "gemini"}
  }
}
```

**Criterios de Aceptación:**
- [ ] CA-1: `/health` responde 200 con todo operativo
- [ ] CA-2: Si DB cae, responde 503 con detalle
- [ ] CA-3: Logs en formato JSON con `request_id`
- [ ] CA-4: Excepción no manejada retorna 500 sin filtrar stack trace

---

### US-004: Deploy a Railway

**Estimación:** 2 hrs | **Prioridad:** Alta

**Como** desarrollador
**Quiero** deploy automático desde GitHub
**Para que** los cambios lleguen a producción sin fricción

**Requisitos Funcionales:**
- RF-1. Proyecto Railway conectado a repo GitHub
- RF-2. Deploy automático en push a `main`
- RF-3. Variables de entorno configuradas
- RF-4. Redis addon provisionado
- RF-5. Dominio HTTPS asignado

**Criterios de Aceptación:**
- [ ] CA-1: Push a `main` dispara deploy automático
- [ ] CA-2: `/health` accesible por HTTPS público
- [ ] CA-3: Logs visibles en Railway dashboard
- [ ] CA-4: Migraciones corren automáticamente en deploy

---

### US-005: Observabilidad con Sentry

**Estimación:** 1 hr | **Prioridad:** Media

**Como** desarrollador
**Quiero** capturar errores de producción automáticamente
**Para que** pueda arreglarlos antes de que el usuario los reporte

**Requisitos Funcionales:**
- RF-1. Sentry SDK integrado en FastAPI
- RF-2. Captura de excepciones no manejadas
- RF-3. Contexto de usuario (sin datos sensibles)
- RF-4. Filtrado de PII (nombres, teléfonos, datos de salud)

**Criterios de Aceptación:**
- [ ] CA-1: Excepción en producción aparece en Sentry
- [ ] CA-2: Ningún dato de salud aparece en el reporte
- [ ] CA-3: Teléfonos aparecen enmascarados (`+52****1234`)

---

## EP-01 — Capa de Abstracción de IA

---

### US-006: Interface base de proveedores de IA (con soporte de tool-use)

**Estimación:** 4 hrs (↑ desde 3 hrs por soporte de tools — ver ADR-007) | **Prioridad:** Crítica

**Como** desarrollador
**Quiero** una interface abstracta para proveedores de IA que soporte tool-use nativo
**Para que** pueda cambiar de API a modelos locales sin refactor, y para que Koach pueda operar como agente (ADR-007)

**Requisitos Funcionales:**
- RF-1. Clase abstracta `LLMProvider` (ver sección 3.2)
- RF-2. Clase abstracta `TranscriptionProvider`
- RF-3. Clase abstracta `VisionProvider`
- RF-4. DTOs: `Message`, `CompletionRequest`, `CompletionResponse`
- RF-5. Enum `ModelTier` con FAST, SMART, VISION, AUDIO
- RF-6. Excepciones: `ProviderUnavailableError`, `RateLimitError`, `ContentFilterError`
- **RF-7. DTO `ToolDefinition`** (nombre, descripción, JSON schema de input) — formato agnóstico de proveedor, mapeado internamente al formato específico de cada SDK (Anthropic tool use, function calling de Gemini, etc.)
- **RF-8. `CompletionRequest.tools: list[ToolDefinition] | None`** — lista opcional de herramientas disponibles para ese request
- **RF-9. DTO `ToolCall`** (id, nombre de la tool, argumentos parseados como dict) y **`ToolResult`** (tool_call_id, resultado, es_error)
- **RF-10. `CompletionResponse.tool_calls: list[ToolCall] | None`** — cuando el modelo decide invocar herramientas en vez de (o además de) responder texto
- **RF-11. `CompletionResponse.stop_reason`** — enum que distingue `end_turn`, `tool_use`, `max_tokens`, para que el orquestador sepa si debe ejecutar tools y volver a llamar al modelo, o si ya terminó
- **RF-12. Método `continue_with_tool_results()` o equivalente en el contrato de uso** — forma estándar de reenviar los resultados de las tools ejecutadas para que el modelo redacte la respuesta final (multi-turno dentro del mismo turno de conversación)

**Requisitos No Funcionales:**
- RNF-1. Ninguna dependencia de SDKs específicos en `base.py`
- RNF-2. Type hints completos
- **RNF-3. Un provider que no soporte tool-use (p. ej. un modelo local temprano) debe poder declarar `supports_tools = False`** y el `AIRouter` debe respetarlo (ver US-009 extendida) en vez de fallar en tiempo de ejecución

**Contratos (extensión de la sección 3.2):**
```python
@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: dict  # JSON Schema

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict

@dataclass
class ToolResult:
    tool_call_id: str
    content: str  # resultado serializado, lo que el modelo "ve"
    is_error: bool = False

class StopReason(str, Enum):
    END_TURN = "end_turn"
    TOOL_USE = "tool_use"
    MAX_TOKENS = "max_tokens"

# Extensión de CompletionRequest y CompletionResponse (sección 3.2):
# CompletionRequest.tools: list[ToolDefinition] | None = None
# CompletionResponse.tool_calls: list[ToolCall] | None = None
# CompletionResponse.stop_reason: StopReason = StopReason.END_TURN
```

**Criterios de Aceptación:**
- [ ] CA-1: `LLMProvider` no importa `anthropic` ni `google.generativeai`
- [ ] CA-2: Se puede crear un provider ficticio implementando la interface
- [ ] CA-3: `mypy` valida las implementaciones correctamente
- [ ] **CA-4: Un `CompletionRequest` con `tools` no vacío, contra `AnthropicProvider`, retorna `tool_calls` cuando el modelo decide usar una herramienta**
- [ ] **CA-5: Un provider con `supports_tools = False` rechaza (con excepción clara) un request que incluya `tools`, en vez de ignorarlos silenciosamente**

**Notas técnicas:** Esta US es la base de todo el sistema de IA y ahora también la base del sistema agéntico (ADR-007). Invertir tiempo aquí ahorra semanas después. El diseño del DTO de tools debe ser suficientemente genérico para que, al migrar a un modelo local que soporte function calling (p. ej. vía Ollama con modelos compatibles), no haya que tocar `app/services/` ni las definiciones de tools de US-159 — solo el adapter.

---

### US-007: Proveedor Anthropic (Claude)

**Estimación:** 2 hrs | **Prioridad:** Crítica

**Como** sistema
**Quiero** usar Claude para tareas de razonamiento
**Para que** las conversaciones sean de alta calidad

**Requisitos Funcionales:**
- RF-1. `AnthropicProvider` implementa `LLMProvider` y `VisionProvider`
- RF-2. Soporta tiers SMART y VISION
- RF-3. Manejo de rate limits con backoff exponencial
- RF-4. Cálculo de costo por request
- RF-5. Timeout configurable (default 30s)

**Contratos:**
```python
class AnthropicProvider(LLMProvider, VisionProvider):
    def __init__(self, api_key: SecretStr, model_map: dict[ModelTier, str]):
        ...

    @property
    def supported_tiers(self) -> list[ModelTier]:
        return [ModelTier.SMART, ModelTier.VISION]
```

**Criterios de Aceptación:**
- [ ] CA-1: `complete()` retorna respuesta válida de Claude
- [ ] CA-2: `stream()` emite chunks progresivamente
- [ ] CA-3: Rate limit dispara retry con backoff
- [ ] CA-4: `health_check()` detecta API key inválida
- [ ] CA-5: Costo calculado coincide con pricing oficial

---

### US-008: Proveedor Gemini (tareas rápidas)

**Estimación:** 2 hrs | **Prioridad:** Alta

**Como** sistema
**Quiero** usar Gemini Flash para tareas de alto volumen
**Para que** los costos se mantengan bajos

**Requisitos Funcionales:**
- RF-1. `GeminiProvider` implementa `LLMProvider`
- RF-2. Soporta tier FAST
- RF-3. Modo JSON estructurado para extracción de datos

**Criterios de Aceptación:**
- [ ] CA-1: Clasifica tipo de mensaje en < 500ms
- [ ] CA-2: Modo JSON retorna estructura válida
- [ ] CA-3: Costo por request registrado

---

### US-009: Router de IA con fallback (con soporte de tool-calling)

**Estimación:** 3 hrs (↑ desde 2 hrs por manejo de tools — ver ADR-007) | **Prioridad:** Crítica

**Como** sistema
**Quiero** seleccionar automáticamente el proveedor adecuado, incluyendo cuándo el request lleva herramientas
**Para que** cada tarea use el modelo correcto al costo correcto, y el loop agéntico (US-160) tenga un único punto de entrada

**Requisitos Funcionales:**
- RF-1. `AIRouter` registra proveedores según `AI_STRATEGY`
- RF-2. Selecciona proveedor por `ModelTier`
- RF-3. Fallback automático si el primario falla
- RF-4. Flag `prefer_local` para forzar modelos locales (futuro)
- RF-5. Registro de métricas: latencia, tokens, costo por tarea
- **RF-6. Si `request.tools` no está vacío, el router solo considera proveedores con `supports_tools = True`** — si el proveedor configurado para ese tier no soporta tools, escala al fallback en vez de enviar el request sin tools silenciosamente
- **RF-7. El fallback de un request con tools debe ir a otro proveedor que también soporte tools** — nunca degradar silenciosamente a un proveedor sin tools cuando la tarea las requiere (eso rompería el loop agéntico a medias)
- **RF-8. Métrica adicional: número de tool_calls por respuesta y qué tools se invocaron** — necesario para el dashboard de costos/uso y para detectar abuso o loops raros de tool-calling

**Flujos:**
```
complete(request, tier=SMART)
  → provider = anthropic (por config)
  → try: anthropic.complete()
  → except ProviderUnavailable:
      → fallback = gemini
      → gemini.complete()

# Con tools (nuevo):
complete(request_con_tools, tier=SMART)
  → provider = anthropic (soporta tools, por config)
  → try: anthropic.complete(request_con_tools)
  → except ProviderUnavailable:
      → fallback = siguiente provider con supports_tools=True
      → si no existe ninguno → ProviderUnavailableError explícito
        (NO se reintenta sin tools: el llamador decide qué hacer)
```

**Criterios de Aceptación:**
- [ ] CA-1: Tier FAST rutea a Gemini, SMART a Anthropic
- [ ] CA-2: Si Anthropic cae, SMART usa fallback sin error al usuario
- [ ] CA-3: Cambiar `AI_SMART_PROVIDER` en `.env` cambia el ruteo
- [ ] CA-4: Métricas registradas en logs estructurados
- [ ] **CA-5: Request con `tools` nunca se rutea a un proveedor con `supports_tools = False`**
- [ ] **CA-6: Si ningún proveedor disponible soporta tools, se lanza `ProviderUnavailableError` explícito (no se envía el request sin tools)**
- [ ] **CA-7: Logs incluyen qué tools fueron invocadas por el modelo en cada respuesta**

---

### US-010: Sistema de prompts versionados

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** desarrollador
**Quiero** prompts en archivos separados y versionados
**Para que** pueda iterar sin cambiar código y hacer A/B testing

**Requisitos Funcionales:**
- RF-1. Prompts en YAML con metadata (versión, autor, fecha)
- RF-2. Templating con Jinja2 para variables
- RF-3. `PromptLoader` con caché en memoria
- RF-4. Validación de variables requeridas
- RF-5. Soporte de prompts por perfil de usuario (futuro EP-26)

**Contratos:**
```yaml
# app/ai/prompts/system/koach_base.yaml
name: koach_base
version: "1.0.0"
description: System prompt base del agente Koach
variables:
  - nombre
  - meta
  - calorias_meta
  - tono
content: |
  Eres "Koach", un coach de salud proactivo especializado
  en fitness y nutrición para mexicanos con vida ocupada.

  CONTEXTO DEL USUARIO:
  - Nombre: {{ nombre }}
  - Meta: {{ meta }}
  - Plan: {{ calorias_meta }} kcal
  - Tono: {{ tono }}

  REGLAS DE SEGURIDAD (CRÍTICO — NUNCA VIOLAR):
  1. NO ERES MÉDICO...
```

```python
# Uso
prompt = prompt_loader.render(
    "system/koach_base",
    nombre="Jaziel",
    meta="bajar_peso",
    calorias_meta=2200,
    tono="coach",
)
```

**Criterios de Aceptación:**
- [ ] CA-1: Prompt se carga y renderiza con variables
- [ ] CA-2: Variable faltante lanza error claro
- [ ] CA-3: Cambiar el YAML no requiere reiniciar (modo dev)
- [ ] CA-4: Prompts versionados en git con historial

---

## EP-02 — Landing Web

---

### US-011: Setup Next.js y deploy

**Estimación:** 2 hrs | **Prioridad:** Alta

**Como** visitante
**Quiero** acceder a koach.mx
**Para que** pueda conocer el producto

**Requisitos Funcionales:**
- RF-1. Next.js 14 con App Router y TypeScript
- RF-2. Tailwind con design tokens de Koach
- RF-3. Deploy en Vercel conectado a GitHub
- RF-4. Dominio koach.mx apuntando a Vercel

**Design tokens:**
```js
colors: {
  primary: '#10B981',    // Verde salud
  dark: '#1E293B',       // Azul oscuro
  accent: '#F59E0B',     // Ámbar energía
  surface: '#FAFAFA',
}
```

**Criterios de Aceptación:**
- [ ] CA-1: koach.mx carga con HTTPS
- [ ] CA-2: Lighthouse score > 90 en Performance
- [ ] CA-3: Deploy automático en push

---

### US-012: Landing page principal

**Estimación:** 4 hrs | **Prioridad:** Alta

**Como** visitante interesado
**Quiero** entender qué es Koach en 30 segundos
**Para que** decida si me interesa probarlo

**Requisitos Funcionales:**
- RF-1. Hero con propuesta de valor y CTA a WhatsApp
- RF-2. Sección problema (3 puntos)
- RF-3. Sección cómo funciona (3 pasos)
- RF-4. Mockups de conversación de WhatsApp
- RF-5. Sección precios con plan Founder destacado
- RF-6. FAQ (10 preguntas)
- RF-7. Footer con links legales

**Criterios de Aceptación:**
- [ ] CA-1: CTA abre WhatsApp con mensaje pre-llenado
- [ ] CA-2: Responsive perfecto en móvil (>90% del tráfico)
- [ ] CA-3: Metadata SEO y Open Graph configurados

---

### US-013: Captura de leads

**Estimación:** 1 hr | **Prioridad:** Media

**Como** visitante no listo para probar
**Quiero** dejar mi email
**Para que** me avisen cuando esté disponible

**Requisitos Funcionales:**
- RF-1. Formulario: email, nombre, meta principal
- RF-2. Validación con Zod
- RF-3. Guardar en tabla `leads_iniciales` de Supabase
- RF-4. Confirmación visual al enviar

**Criterios de Aceptación:**
- [ ] CA-1: Lead se guarda en Supabase
- [ ] CA-2: Email duplicado no crea registro nuevo
- [ ] CA-3: Errores de red muestran mensaje claro

---

### US-014: Páginas legales

**Estimación:** 1 hr | **Prioridad:** Alta

**Como** usuario preocupado por privacidad
**Quiero** leer cómo manejan mis datos
**Para que** decida con información

**Requisitos Funcionales:**
- RF-1. `/privacidad` — Aviso de Privacidad LFPDPPP 2025
- RF-2. `/terminos` — Términos y Condiciones
- RF-3. `/disclaimer-medico` — Disclaimer formal
- RF-4. Versionado de documentos con fecha

**Criterios de Aceptación:**
- [ ] CA-1: Documentos accesibles desde footer
- [ ] CA-2: Incluyen todos los elementos requeridos por LFPDPPP
- [ ] CA-3: Fecha de última actualización visible

---

# 12. FASE 1 — MVP WHATSAPP

## EP-03 — Canal WhatsApp

---

### US-015: Interface abstracta de mensajería

**Estimación:** 2 hrs | **Prioridad:** Crítica

**Como** desarrollador
**Quiero** una abstracción del canal de mensajería
**Para que** pueda agregar chat en app (Fase 4) sin refactor

**Requisitos Funcionales:**
- RF-1. Interface `MessagingChannel` con `send_text`, `send_buttons`, `send_document`
- RF-2. DTO `IncomingMessage` normalizado (agnóstico de canal)
- RF-3. Enum `MessageType`: TEXT, AUDIO, IMAGE, BUTTON_REPLY, DOCUMENT

**Contratos:**
```python
class MessagingChannel(ABC):
    @abstractmethod
    async def send_text(self, to: str, text: str) -> str: ...

    @abstractmethod
    async def send_buttons(
        self, to: str, text: str, buttons: list[Button]
    ) -> str: ...

    @abstractmethod
    async def send_document(
        self, to: str, url: str, caption: str | None
    ) -> str: ...

    @abstractmethod
    async def send_template(
        self, to: str, template_name: str, variables: dict
    ) -> str: ...


@dataclass
class IncomingMessage:
    channel: Literal["whatsapp", "app"]
    from_id: str           # phone o user_id
    message_id: str
    type: MessageType
    text: str | None
    media_url: str | None
    button_payload: str | None
    timestamp: datetime
```

**Criterios de Aceptación:**
- [ ] CA-1: `WhatsAppChannel` implementa la interface
- [ ] CA-2: Lógica de negocio no importa nada de WhatsApp
- [ ] CA-3: Mock channel funciona en tests

---

### US-016: Webhook de WhatsApp

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** sistema
**Quiero** recibir mensajes de WhatsApp
**Para que** el agente pueda responder

**Requisitos Funcionales:**
- RF-1. `GET /webhooks/whatsapp` para verificación de Meta
- RF-2. `POST /webhooks/whatsapp` para recibir eventos
- RF-3. Validación de firma HMAC (seguridad)
- RF-4. Parseo a `IncomingMessage`
- RF-5. Deduplicación por `message_id`
- RF-6. Respuesta 200 inmediata, procesamiento asíncrono

**Requisitos No Funcionales:**
- RNF-1. Responder < 5 segundos (requisito de Meta)
- RNF-2. Procesamiento en background con Celery

**Flujos:**
```
Meta → POST /webhooks/whatsapp
  → Validar firma
  → Parsear payload
  → Verificar duplicado (Redis, TTL 24h)
  → Encolar tarea Celery
  → Responder 200 OK
      ↓ (async)
  Worker procesa mensaje
```

**Criterios de Aceptación:**
- [ ] CA-1: Verificación de Meta pasa correctamente
- [ ] CA-2: Firma inválida retorna 403
- [ ] CA-3: Mensaje duplicado se ignora
- [ ] CA-4: Respuesta en < 500ms
- [ ] CA-5: Mensaje de texto, audio e imagen se parsean correctamente

---

### US-017: Envío de mensajes de texto

**Estimación:** 2 hrs | **Prioridad:** Crítica

**Como** agente
**Quiero** enviar mensajes al usuario
**Para que** pueda comunicarme

**Requisitos Funcionales:**
- RF-1. `send_text()` funcional
- RF-2. Manejo de errores de la API de Meta
- RF-3. Reintentos con backoff
- RF-4. Registro en `historial_conversacion`
- RF-5. Split automático si el mensaje excede 4096 chars

**Criterios de Aceptación:**
- [ ] CA-1: Mensaje llega al WhatsApp del usuario
- [ ] CA-2: Error de red dispara reintento
- [ ] CA-3: Mensaje se registra con `message_id` de Meta
- [ ] CA-4: Mensaje largo se divide sin cortar palabras

---

### US-018: Botones interactivos

**Estimación:** 2 hrs | **Prioridad:** Alta

**Como** usuario
**Quiero** responder con un tap
**Para que** registrar sea rápido

**Requisitos Funcionales:**
- RF-1. `send_buttons()` con hasta 3 botones (límite de Meta)
- RF-2. Payload personalizado por botón
- RF-3. Parseo de respuesta de botón en webhook

**Ejemplo:**
```python
await channel.send_buttons(
    to=phone,
    text="¿Ya hiciste tu rutina de hoy?",
    buttons=[
        Button(id="ejercicio_completo", title="✅ Completa"),
        Button(id="ejercicio_parcial", title="⚡ Parcial"),
        Button(id="ejercicio_no", title="❌ No pude"),
    ],
)
```

**Criterios de Aceptación:**
- [ ] CA-1: Botones se renderizan en WhatsApp
- [ ] CA-2: Tap en botón llega como `BUTTON_REPLY` con payload
- [ ] CA-3: Más de 3 botones lanza error claro en desarrollo

---

### US-019: Templates de Meta

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** agente
**Quiero** iniciar conversaciones proactivamente
**Para que** pueda buscar al usuario (core del producto)

**Requisitos Funcionales:**
- RF-1. `send_template()` con variables
- RF-2. Registro de templates aprobados en DB
- RF-3. Detección de ventana de 24h (si abierta, texto libre; si no, template)
- RF-4. Fallback si template rechazado

**Modelo de datos:**
```sql
CREATE TABLE whatsapp_templates (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    meta_status VARCHAR(20),  -- approved, pending, rejected
    language VARCHAR(10) DEFAULT 'es_MX',
    variables JSONB,
    body_text TEXT,
    categoria VARCHAR(50),
    created_at TIMESTAMP
);
```

**Criterios de Aceptación:**
- [ ] CA-1: Template aprobado se envía correctamente
- [ ] CA-2: Con ventana abierta se usa texto libre (más barato)
- [ ] CA-3: Con ventana cerrada se usa template automáticamente
- [ ] CA-4: Template no aprobado lanza error antes de enviar

---

## EP-04 — Onboarding Conversacional

---

### US-020: Máquina de estados de conversación

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** sistema
**Quiero** mantener el estado de flujos multi-paso
**Para que** el onboarding funcione correctamente

**Requisitos Funcionales:**
- RF-1. Tabla `conversacion_estado` con estado actual y contexto
- RF-2. Máquina de estados con transiciones definidas
- RF-3. Timeout de estado (24h sin respuesta → reset suave)
- RF-4. Capacidad de reanudar donde se quedó

**Modelo de datos:**
```sql
CREATE TABLE conversacion_estado (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    flujo VARCHAR(50),           -- 'onboarding', 'registro_comida', etc.
    paso_actual VARCHAR(50),
    contexto JSONB,              -- datos parciales del flujo
    intentos INT DEFAULT 0,
    ultima_interaccion TIMESTAMP,
    expira_at TIMESTAMP
);
```

**Criterios de Aceptación:**
- [ ] CA-1: Usuario nuevo entra en estado `onboarding.inicio`
- [ ] CA-2: Respuesta válida avanza al siguiente paso
- [ ] CA-3: Respuesta inválida reintenta con mensaje de ayuda
- [ ] CA-4: 3 intentos fallidos escala a mensaje de soporte
- [ ] CA-5: Usuario puede reanudar después de horas

---

### US-021: Consentimiento LFPDPPP

**Estimación:** 2 hrs | **Prioridad:** Crítica

**Como** empresa
**Quiero** consentimiento expreso documentado
**Para que** cumplamos la ley de datos de salud

**Requisitos Funcionales:**
- RF-1. Primer paso del onboarding: aviso + solicitud de consentimiento
- RF-2. Usuario debe responder "ACEPTO" explícitamente
- RF-3. Registro en tabla `consentimientos` con timestamp, versión, IP
- RF-4. Si no acepta, no continuar onboarding
- RF-5. Link al aviso completo en koach.mx/privacidad

**Flujo:**
```
Koach: "¡Hola! Soy Koach 👋 Antes de empezar necesito tu permiso.

Voy a guardar datos sobre tu salud (peso, alergias, hábitos) para
poder ayudarte. Puedes pedirme que los borre cuando quieras
escribiendo BORRAR MIS DATOS.

Lee el aviso completo: koach.mx/privacidad

¿Aceptas? Responde ACEPTO para continuar."

Usuario: "ACEPTO"

Koach: "Perfecto ✅ Empecemos..."
```

**Criterios de Aceptación:**
- [ ] CA-1: Sin "ACEPTO" no avanza el flujo
- [ ] CA-2: Consentimiento registrado con versión del documento
- [ ] CA-3: Respuesta ambigua ("ok", "sí") pide confirmación explícita

---

### US-022: Verificación de mayoría de edad

**Estimación:** 1 hr | **Prioridad:** Crítica

**Como** empresa
**Quiero** verificar que el usuario es mayor de 18
**Para que** no atendamos menores (riesgo legal y ético)

**Requisitos Funcionales:**
- RF-1. Pregunta explícita de mayoría de edad
- RF-2. Si responde "no", mensaje respetuoso y cierre
- RF-3. Registro de confirmación en `users.mayor_edad_confirmado`
- RF-4. Si durante uso se detecta que es menor, suspender cuenta

**Criterios de Aceptación:**
- [ ] CA-1: Respuesta negativa termina el onboarding con respeto
- [ ] CA-2: Confirmación registrada en DB
- [ ] CA-3: Edad declarada < 18 en paso posterior también bloquea

---

### US-023: Flujo de 5 preguntas básicas

**Estimación:** 4 hrs | **Prioridad:** Crítica

**Como** usuario nuevo
**Quiero** registrarme en 5 minutos
**Para que** obtenga valor rápido

**Requisitos Funcionales:**
- RF-1. Secuencia: nombre → edad+género → peso+talla → meta → alergias
- RF-2. Validación de cada respuesta con rangos razonables
- RF-3. Parseo flexible ("mido 1.75", "175cm", "1 metro 75")
- RF-4. Botones para meta (opciones fijas)
- RF-5. Guardar en `perfiles` progresivamente

**Validaciones:**
```python
EDAD_MIN, EDAD_MAX = 18, 100
PESO_MIN_KG, PESO_MAX_KG = 35, 300
TALLA_MIN_CM, TALLA_MAX_CM = 130, 230
```

**Flujos alternativos:**
- Valor fuera de rango → pedir confirmación
- Respuesta no parseable → reformular pregunta con ejemplo
- Usuario escribe algo no relacionado → responder brevemente y retomar

**Criterios de Aceptación:**
- [ ] CA-1: Onboarding completo en < 5 min
- [ ] CA-2: "mido 1.75" y "175" se parsean igual
- [ ] CA-3: Peso de 500kg pide confirmación
- [ ] CA-4: Perfil queda completo en DB al finalizar
- [ ] CA-5: Usuario puede corregir un dato diciendo "me equivoqué"

---

### US-024: PAR-Q y liberación médica

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** empresa responsable
**Quiero** detectar condiciones médicas de riesgo
**Para que** no generemos rutinas peligrosas

**Requisitos Funcionales:**
- RF-1. Cuestionario PAR-Q simplificado (7 preguntas sí/no)
- RF-2. Si alguna respuesta es "sí" → `parq_pendiente_medico = true`
- RF-3. Con PAR-Q pendiente, NO generar rutinas de ejercicio
- RF-4. Sí generar plan nutricional (menor riesgo)
- RF-5. Mensaje claro explicando por qué

**Preguntas PAR-Q:**
1. ¿Algún médico te ha dicho que tienes un problema del corazón?
2. ¿Sientes dolor en el pecho al hacer actividad física?
3. ¿Has perdido el equilibrio por mareos o perdido el conocimiento?
4. ¿Tienes algún problema de huesos o articulaciones que empeore con actividad?
5. ¿Tu médico te receta medicamentos para presión arterial o el corazón?
6. ¿Tienes alguna otra razón por la que no deberías hacer actividad física?
7. ¿Estás embarazada actualmente?

**Criterios de Aceptación:**
- [ ] CA-1: Respuesta "sí" en cualquier pregunta bloquea rutinas
- [ ] CA-2: Usuario recibe explicación empática, no alarmista
- [ ] CA-3: Puede desbloquearse confirmando liberación médica
- [ ] CA-4: Estado registrado en `perfiles.parq_*`

---

### US-025: Mensaje de bienvenida y capacidades

**Estimación:** 2 hrs | **Prioridad:** Alta

**Como** usuario recién registrado
**Quiero** saber qué puede hacer Koach
**Para que** aproveche el producto

**Requisitos Funcionales:**
- RF-1. Mensaje resumen de capacidades al terminar onboarding
- RF-2. Comando `AYUDA` muestra el mismo mensaje
- RF-3. Formato escaneable con emojis
- RF-4. Disclaimer médico incluido

**Criterios de Aceptación:**
- [ ] CA-1: Mensaje < 10 líneas
- [ ] CA-2: `AYUDA` funciona en cualquier momento
- [ ] CA-3: Incluye disclaimer de no ser médico

---

## EP-05 — Generación de Planes

---

### US-026: Cálculo de TDEE y macros (dominio puro)

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** sistema
**Quiero** calcular necesidades calóricas con base científica
**Para que** los planes sean seguros y efectivos

**Requisitos Funcionales:**
- RF-1. Fórmula Mifflin-St Jeor para TMB
- RF-2. Factores de actividad estándar
- RF-3. Ajuste por meta (déficit/superávit)
- RF-4. Distribución de macros según guías
- RF-5. Validación de mínimos seguros

**Requisitos No Funcionales:**
- RNF-1. Lógica pura, sin IA ni dependencias externas
- RNF-2. 100% testeable
- RNF-3. Determinista (mismo input → mismo output)

**Contratos:**
```python
# app/domain/services/tdee_calculator.py

def calcular_tmb(perfil: PerfilFisico) -> float:
    """Mifflin-St Jeor."""
    base = 10 * perfil.peso_kg + 6.25 * perfil.talla_cm - 5 * perfil.edad
    return base + 5 if perfil.genero == Genero.MASCULINO else base - 161


def calcular_tdee(tmb: float, nivel: NivelActividad) -> float:
    return tmb * NIVEL_ACTIVIDAD_FACTORES[nivel]


def calcular_objetivo_calorico(tdee: float, meta: Meta) -> int:
    """Aplica déficit/superávit con límites de seguridad."""
    ...


def distribuir_macros(
    calorias: int, peso_kg: float, meta: Meta
) -> DistribucionMacros:
    """Proteína 1.6-2.2g/kg, grasas 20-30%, carbs el resto."""
    ...
```

**Reglas de seguridad:**
```python
CALORIAS_MIN_MUJER = 1200
CALORIAS_MIN_HOMBRE = 1500
PERDIDA_MAX_SEMANAL_PCT = 1.0  # % del peso corporal
```

**Criterios de Aceptación:**
- [ ] CA-1: Hombre 30 años, 80kg, 175cm, sedentario → TDEE ~2200 kcal
- [ ] CA-2: Mujer con déficit nunca baja de 1200 kcal
- [ ] CA-3: Proteína siempre entre 1.6-2.2 g/kg
- [ ] CA-4: Suma de macros × sus calorías = total calórico (±2%)
- [ ] CA-5: 20+ tests unitarios cubriendo casos límite

**Notas técnicas:** Esta US es lógica pura de dominio. NO usa IA. Los cálculos deben ser reproducibles y auditables.

---

### US-027: Generación de plan nutricional

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** usuario
**Quiero** un plan de comidas personalizado
**Para que** sepa qué comer

**Requisitos Funcionales:**
- RF-1. Usa macros calculados en US-026
- RF-2. IA genera ejemplos de comidas con contexto mexicano
- RF-3. Respeta alergias y restricciones declaradas
- RF-4. Distribuye en 5 tiempos de comida
- RF-5. Guarda en `plan_nutricional`

**Requisitos No Funcionales:**
- RNF-1. Usa `AIRouter` con tier SMART
- RNF-2. Prompt en `app/ai/prompts/tasks/generar_plan_nutricional.yaml`
- RNF-3. Output validado con Pydantic

**Contratos:**
```python
class ComidaSugerida(BaseModel):
    nombre: str
    ingredientes: list[str]
    calorias: int
    proteina_g: int
    carbs_g: int
    grasas_g: int
    tiempo_preparacion_min: int


class PlanNutricionalGenerado(BaseModel):
    calorias_meta: int
    macros: DistribucionMacros
    desayuno: list[ComidaSugerida]      # 3 opciones
    colacion_am: list[ComidaSugerida]
    comida: list[ComidaSugerida]
    colacion_pm: list[ComidaSugerida]
    cena: list[ComidaSugerida]
    notas: str
```

**Criterios de Aceptación:**
- [ ] CA-1: Plan generado respeta macros calculados (±5%)
- [ ] CA-2: Ningún alimento alérgeno aparece en el plan
- [ ] CA-3: Al menos 60% de ingredientes son accesibles en México
- [ ] CA-4: Output parsea correctamente a `PlanNutricionalGenerado`
- [ ] CA-5: Si la IA falla, se usa plan template de respaldo

---

### US-028: Generación de plan de ejercicio

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** usuario
**Quiero** una rutina adaptada a mi situación
**Para que** pueda empezar a entrenar

**Requisitos Funcionales:**
- RF-1. Considera: objetivo, tiempo disponible, equipamiento, nivel
- RF-2. Respeta lesiones declaradas
- RF-3. NO genera si `parq_pendiente_medico = true`
- RF-4. Rutina semanal con días de descanso
- RF-5. Ejercicios referencian `ejercicios_biblioteca` (US-055)

**Criterios de Aceptación:**
- [ ] CA-1: Con PAR-Q pendiente no genera y explica por qué
- [ ] CA-2: Lesión de rodilla → sin sentadillas profundas ni impacto
- [ ] CA-3: "Sin equipo" → solo ejercicios de peso corporal
- [ ] CA-4: Rutina incluye calentamiento y enfriamiento
- [ ] CA-5: Al menos 1 día de descanso por semana

---

### US-029: Entrega de planes en WhatsApp

**Estimación:** 2 hrs | **Prioridad:** Alta

**Como** usuario
**Quiero** recibir mi plan de forma legible
**Para que** pueda usarlo

**Requisitos Funcionales:**
- RF-1. Resumen corto en WhatsApp (< 10 líneas)
- RF-2. Formato con emojis para escaneo rápido
- RF-3. Mención de que el PDF completo llegará después
- RF-4. Split en varios mensajes si es necesario

**Criterios de Aceptación:**
- [ ] CA-1: Mensaje legible en pantalla de móvil sin scroll excesivo
- [ ] CA-2: Formato consistente con el tono del usuario

---

### US-030: PDF de plan inicial

**Estimación:** 3 hrs | **Prioridad:** Media

**Como** usuario
**Quiero** un PDF profesional de mi plan
**Para que** pueda consultarlo e imprimirlo

**Requisitos Funcionales:**
- RF-1. Generación con WeasyPrint desde template HTML+CSS
- RF-2. Branding de Koach (colores, logo)
- RF-3. Incluye: datos, TDEE explicado, macros, ejemplos de comidas, rutina
- RF-4. Disclaimer médico visible
- RF-5. Subir a Supabase Storage y enviar por WhatsApp

**Criterios de Aceptación:**
- [ ] CA-1: PDF se genera en < 5 segundos
- [ ] CA-2: Se ve profesional en móvil y desktop
- [ ] CA-3: URL firmada expira en 7 días
- [ ] CA-4: Llega como documento adjunto en WhatsApp

---

## EP-06 — Registro de Actividad

---

### US-031: Pre-filtro de comandos exactos y screening de crisis (alcance reducido — ver ADR-007)

**Estimación:** 2 hrs (↓ desde 3 hrs — dejó de ser el router principal, ver ADR-007) | **Prioridad:** Crítica

> **⚠️ Cambio de diseño (ADR-007):** esta US originalmente clasificaba TODO mensaje entrante en una categoría (`registro_comida`, `registro_ejercicio`, etc.) y actuaba como router principal hacia handlers específicos. Con la arquitectura agéntica, ese ruteo lo hace el propio Claude eligiendo tools dentro del loop de US-160. Esta US se reduce a las dos cosas que SÍ conviene resolver antes de gastar una llamada a tier SMART con el set completo de tools: comandos exactos y pre-screening de crisis. Las categorías de "intención" como concepto de negocio (registro_comida, pregunta_salud, etc.) siguen existiendo, pero como metadata de logging/analítica derivada de qué tool se invocó, no como decisión de ruteo previa.

**Como** sistema
**Quiero** resolver comandos exactos sin gastar una llamada a IA, y detectar señales de crisis antes de entrar al loop agéntico
**Para que** el sistema sea eficiente en costo y la detección de crisis (US-032) mantenga su prioridad absoluta e independiente de cualquier tool

**Requisitos Funcionales:**
- RF-1. Detección de comandos exactos (`AYUDA`, `PAUSA`, `REANUDAR`, `BORRAR MIS DATOS`, `MIS DATOS`, etc.) por coincidencia de texto — **sin llamar a IA**, resuelto en código
- RF-2. Pre-screening de crisis con tier FAST (palabras clave + heurística barata) como primer filtro; si hay señal ambigua, escala a la verificación completa de tier SMART de US-032 (nunca se decide "no es crisis" solo con tier FAST)
- RF-3. Si no es comando exacto ni señal de crisis, el mensaje pasa tal cual al loop agéntico (US-160) — **ya no se clasifica en una categoría de intención antes de eso**
- RF-4. Metadata de intención (para analítica, no para ruteo) se deriva DESPUÉS del turno, a partir de qué tool(s) invocó el modelo, y se registra en `historial_conversacion`

**Contratos:**
```python
class ComandoExacto(str, Enum):
    AYUDA = "AYUDA"
    PAUSA = "PAUSA"
    REANUDAR = "REANUDAR"
    BORRAR_MIS_DATOS = "BORRAR MIS DATOS"
    MIS_DATOS = "MIS DATOS"
    # ...


class PreScreeningResult(BaseModel):
    es_comando_exacto: bool
    comando: ComandoExacto | None
    senal_crisis_posible: bool  # dispara verificación completa de US-032
```

**Criterios de Aceptación:**
- [ ] CA-1: "AYUDA" se resuelve sin llamar a ningún proveedor de IA
- [ ] CA-2: Mensaje con señal ambigua de crisis siempre escala a verificación completa (US-032), nunca se descarta en el pre-filtro
- [ ] CA-3: Mensaje normal ("me comí 3 tacos") pasa sin modificación al loop agéntico
- [ ] CA-4: Pre-filtro completo en < 300ms (más rápido que el clasificador original porque hace menos)
- [ ] CA-5: La categoría de intención derivada post-turno coincide con la tool invocada en > 95% de los casos de prueba

**Dependencias:**
- Bloquea: US-160 (todo mensaje pasa primero por este pre-filtro)
- Relacionado: US-032 (este pre-filtro es la primera línea; US-032 sigue siendo la verificación autoritativa de crisis)

---

### US-032: Detección de crisis (prioridad máxima)

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** empresa responsable
**Quiero** detectar señales de crisis emocional
**Para que** derivemos a ayuda profesional

**Requisitos Funcionales:**
- RF-1. Detección ANTES de cualquier otra clasificación
- RF-2. Palabras clave + análisis semántico con tier SMART
- RF-3. Si detecta crisis, sale del modo coach inmediatamente
- RF-4. Proporciona SAPTEL (55 5259-8121) y 911
- RF-5. Marca usuario con `estado_emocional_flag = 'crisis'`
- RF-6. Suspende mensajes proactivos de fitness por 48h
- RF-7. Notifica al administrador (tú)

**Flujo:**
```
Mensaje entrante
  → PRIMERO: detección de crisis
      → Si crisis: protocolo de crisis, FIN
      → Si no: continuar clasificación normal
```

**Criterios de Aceptación:**
- [ ] CA-1: "ya no quiero seguir" activa protocolo
- [ ] CA-2: "ya no quiero seguir la dieta" NO activa (contexto)
- [ ] CA-3: Respuesta empática sin mencionar fitness
- [ ] CA-4: Recursos de ayuda incluidos
- [ ] CA-5: Mensajes proactivos pausados automáticamente
- [ ] CA-6: Falso positivo es preferible a falso negativo

**Notas técnicas:** Esta US es la más delicada del sistema. Preferir sobre-detección. Revisar todos los casos manualmente en las primeras semanas.

---

### US-033: Registro de comidas por lenguaje natural

**Estimación:** 4 hrs | **Prioridad:** Crítica

**Como** usuario
**Quiero** registrar lo que comí escribiendo normal
**Para que** no tenga que buscar en listas

**Requisitos Funcionales:**
- RF-1. Parseo con tier FAST a estructura
- RF-2. Búsqueda en `alimentos_mexicanos` para macros
- RF-3. Si no encuentra, estimación con tier SMART
- RF-4. Confirmación al usuario con resumen
- RF-5. Guardar en `registros_comida` con confianza

**Contratos:**
```python
class AlimentoParseado(BaseModel):
    nombre: str
    cantidad: float
    unidad: str  # "piezas", "gramos", "tazas", "platos"


class ComidaParseada(BaseModel):
    alimentos: list[AlimentoParseado]
    tipo_comida: TipoComida | None  # inferido por hora si no se dice
    lugar: LugarComida | None
    confianza: float
```

**Ejemplos de entrada:**
```
"me comí 3 tacos de canasta"
"desayuné huevos con frijoles y 2 tortillas"
"comí en la fonda, pollo con arroz y agua de jamaica"
"me eché unas galletas"  → cantidad ambigua, pedir aclaración
```

**Criterios de Aceptación:**
- [ ] CA-1: "3 tacos de canasta" → ~450 kcal registradas
- [ ] CA-2: Tipo de comida se infiere por hora del día
- [ ] CA-3: Cantidad ambigua pide aclaración
- [ ] CA-4: Confirmación en < 3 líneas
- [ ] CA-5: Usuario puede corregir diciendo "no, fueron 2"

---

### US-034: Base de alimentos mexicanos

**Estimación:** 3 hrs | **Prioridad:** Alta

**Como** sistema
**Quiero** datos nutricionales de comida mexicana
**Para que** las estimaciones sean precisas

**Requisitos Funcionales:**
- RF-1. Tabla `alimentos_mexicanos` con 200+ entradas iniciales
- RF-2. Campos: nombre, aliases, porción estándar, macros
- RF-3. Búsqueda fuzzy por nombre y aliases
- RF-4. Categorías para agrupación
- RF-5. Seed inicial con platillos comunes

**Modelo de datos:**
```sql
CREATE TABLE alimentos_mexicanos (
    id UUID PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    aliases JSONB,               -- ["taco de canasta", "taco sudado"]
    categoria VARCHAR(50),
    porcion_estandar_g INT,
    porcion_descripcion VARCHAR(100),  -- "1 taco", "1 taza"
    calorias_por_porcion INT,
    proteina_g DECIMAL(5,2),
    carbs_g DECIMAL(5,2),
    grasas_g DECIMAL(5,2),
    fibra_g DECIMAL(5,2),
    sodio_mg INT,
    fuente VARCHAR(100),         -- "USDA", "INCAP", "estimado"
    verificado BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_alimentos_nombre_trgm
ON alimentos_mexicanos USING gin (nombre gin_trgm_ops);
```

**Seed inicial (categorías):**
- Tortillas y masa (15 items)
- Frijoles y leguminosas (10)
- Carnes y proteínas (25)
- Antojitos (tacos, quesadillas, tamales, etc.) (40)
- Verduras mexicanas (nopal, chayote, calabacita) (20)
- Frutas (20)
- Lácteos (15)
- Bebidas (aguas frescas, refrescos) (20)
- Comida de fonda (platillos completos) (35)

**Criterios de Aceptación:**
- [ ] CA-1: Búsqueda de "taco pastor" encuentra el registro
- [ ] CA-2: Búsqueda con typo "kesadilla" encuentra "quesadilla"
- [ ] CA-3: 200+ alimentos en el seed inicial
- [ ] CA-4: Búsqueda responde en < 50ms

---

### US-035: Registro de ejercicio

**Estimación:** 2 hrs | **Prioridad:** Alta

**Como** usuario
**Quiero** registrar mi entrenamiento
**Para que** Koach sepa mi progreso

**Requisitos Funcionales:**
- RF-1. Botones rápidos: ✅ Completo / ⚡ Parcial / ❌ No pude
- RF-2. Lenguaje natural: "hice 30 min de bici"
- RF-3. Guardar en `registros_ejercicio`
- RF-4. Si "no pude", preguntar razón sin juzgar

**Criterios de Aceptación:**
- [ ] CA-1: Tap en botón registra en < 1 segundo
- [ ] CA-2: "no pude" → respuesta empática con alternativa
- [ ] CA-3: Duración se extrae del texto cuando está presente

---

### US-036: Registro de agua y peso

**Estimación:** 2 hrs | **Prioridad:** Media

**Como** usuario
**Quiero** registrar hidratación y peso
**Para que** vea mi progreso completo

**Requisitos Funcionales:**
- RF-1. Agua: incremento simple ("+1 vaso", botones)
- RF-2. Peso: solicitado semanalmente (lunes)
- RF-3. Peso muestra comparación con semana anterior
- RF-4. Validación de cambios extremos (> 3kg en una semana → confirmar)

**Criterios de Aceptación:**
- [ ] CA-1: "tomé 2 vasos" suma 2 al contador del día
- [ ] CA-2: Peso semanal muestra diferencia y tendencia
- [ ] CA-3: Cambio de 10kg en una semana pide confirmación

---

## EP-06 bis — Núcleo Agéntico (ADR-007)

> Estas dos US son el corazón del rediseño agéntico. US-159 define las herramientas que Claude puede invocar; US-160 es el loop que las orquesta. Dependen de la extensión de US-006/US-009 y deben implementarse después de tener al menos US-033, US-035 y US-036 (las funciones de dominio que las tools van a envolver) y US-031 en su alcance reducido.

---

### US-159: Definición de herramientas (tools) del agente

**Estimación:** 5 hrs | **Prioridad:** Crítica

**Como** desarrollador
**Quiero** un catálogo formal de herramientas que Claude puede invocar, cada una envolviendo una función de dominio/servicio existente
**Para que** el loop agéntico (US-160) tenga un contrato claro y cada tool sea testeable de forma aislada

**Contexto:** Con tool-use nativo (ADR-007), en vez de que el backend decida qué handler llamar según una categoría de intención, se le da a Claude una lista de `ToolDefinition` (RF-7 de US-006) y el modelo decide. Esta US formaliza esa lista inicial para la Fase 1 (MVP WhatsApp). Nuevas fases (Fase 2+) agregan más tools sin modificar esta US.

**Requisitos Funcionales:**
- RF-1. Catálogo inicial de tools (Fase 1), cada una con nombre, descripción para el modelo, JSON schema de input, y la función de dominio a la que llama:

| Tool | Descripción (para el modelo) | Llama a | Tipo |
|------|------------------------------|---------|------|
| `registrar_comida` | Registra un alimento o comida que el usuario reporta haber consumido | `meal_service.register_meal()` (US-033) | Escritura |
| `registrar_ejercicio` | Registra una sesión de ejercicio reportada por el usuario | `workout_service.register_workout()` (US-035) | Escritura |
| `registrar_agua` | Suma vasos/litros de agua al contador del día | `hydration_service.add_water()` (US-036) | Escritura |
| `registrar_peso` | Registra el peso corporal reportado, con validación de cambios extremos | `progress_service.register_weight()` (US-036) | Escritura sensible |
| `consultar_alacena` | Consulta qué ingredientes tiene el usuario disponibles | `pantry_service.get_pantry()` (Fase 2, EP-09) | Lectura |
| `sugerir_comida` | Genera 1-3 opciones de comida priorizando alacena y preferencias | `meal_service.suggest_meals()` (Fase 2) | Lectura/generación |
| `ajustar_horario_mensajes` | Cambia el horario en que el usuario prefiere recibir mensajes proactivos | `proactive_service.update_schedule()` (EP-07) | Escritura |
| `activar_modo_silencio` | Pausa temporalmente los mensajes proactivos | `proactive_service.set_silence_mode()` (EP-07) | Escritura |
| `derivar_a_profesional` | Marca que el tema requiere derivación a nutriólogo/médico y genera el mensaje de derivación | `referral_service.flag_referral()` | Escritura sensible |
| `marcar_crisis` | Registra bandera de crisis emocional y dispara protocolo (nunca reemplaza a US-032, es el registro post-detección) | `safety_service.flag_crisis()` (US-032) | Escritura sensible — solo se invoca dentro del protocolo de US-032, no libremente desde el loop normal |

- RF-2. Cada tool define su `input_schema` (JSON Schema) validado con Pydantic antes de ejecutar la función de dominio — **nunca se ejecuta una función de dominio con argumentos no validados, aunque vengan "del modelo"**
- RF-3. Cada tool retorna un `ToolResult` con un resumen legible del resultado (lo que el modelo necesita para redactar la respuesta final), no el objeto de dominio crudo
- RF-4. Las tools marcadas "Escritura sensible" (`registrar_peso`, `derivar_a_profesional`, `marcar_crisis`) tienen una capa adicional de validación determinista en la función de dominio (ver ADR-007, principio de defense-in-depth) — por ejemplo `registrar_peso` rechaza (pide confirmación explícita al usuario en el siguiente turno) un delta > 15% respecto al último registro
- RF-5. El set de tools expuesto a Claude en cada request se filtra según: fase del producto habilitada (p. ej. `consultar_alacena` no existe hasta EP-09), y estado de la cuenta del usuario (p. ej. sin PAR-Q liberado, no se expone ninguna tool de ejercicio)
- RF-6. Registro de auditoría: cada invocación de tool (nombre, argumentos, resultado, timestamp, éxito/error) se guarda en `historial_conversacion` o tabla dedicada `tool_calls_log`

**Modelo de datos:**
```sql
CREATE TABLE tool_calls_log (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    conversacion_turno_id UUID,
    tool_name VARCHAR(50) NOT NULL,
    arguments JSONB NOT NULL,
    result_summary TEXT,
    es_error BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);
```

**Contratos:**
```python
# app/ai/tools/registry.py

TOOL_REGISTRY: dict[str, ToolSpec] = {
    "registrar_comida": ToolSpec(
        definition=ToolDefinition(
            name="registrar_comida",
            description="Registra un alimento o comida que el usuario reporta haber consumido.",
            input_schema={...},  # JSON Schema
        ),
        handler=registrar_comida_handler,  # async fn(user_id, args) -> ToolResult
        requiere_fase="Fase 1",
        requiere_estado_cuenta=None,
    ),
    "registrar_peso": ToolSpec(
        definition=ToolDefinition(...),
        handler=registrar_peso_handler,
        requiere_fase="Fase 1",
        requiere_estado_cuenta=None,
        es_sensible=True,  # activa validación extra determinista
    ),
    # ...
}

def get_tools_for_user(user: User, fase_habilitada: str) -> list[ToolDefinition]:
    """Filtra el catálogo según fase y estado de cuenta (RF-5)."""
    ...
```

**Criterios de Aceptación:**
- [ ] CA-1: Las 10 tools de Fase 1 están definidas con schema válido
- [ ] CA-2: Ejecutar una tool con argumentos que no cumplen el schema lanza error de validación ANTES de tocar la función de dominio
- [ ] CA-3: `registrar_peso` con delta > 15% no se aplica directamente — retorna un `ToolResult` pidiendo confirmación
- [ ] CA-4: `get_tools_for_user()` no incluye tools de ejercicio si `parq_pendiente_medico = true`
- [ ] CA-5: Toda invocación de tool queda en `tool_calls_log`, incluso las que fallan
- [ ] CA-6: `marcar_crisis` no es invocable desde un turno normal — solo desde el flujo de US-032

**Dependencias:**
- Requiere: US-006 extendida (tool-use en `LLMProvider`), US-033, US-035, US-036 (funciones de dominio que las tools envuelven)
- Bloquea: US-160

**Fuera de alcance:** Tools de Fase 2+ (`consultar_alacena`, `sugerir_comida` en su versión completa con negociación conversacional) se definen aquí como placeholder de esquema pero se implementan completas en EP-09/EP-10.

---

### US-160: Bucle agéntico principal (agentic loop)

**Estimación:** 5 hrs | **Prioridad:** Crítica

**Como** sistema
**Quiero** un loop que reciba el mensaje del usuario, decida con Claude qué tool(s) invocar, las ejecute, y redacte la respuesta final
**Para que** Koach opere como agente real y no como un árbol de decisiones clasificado a mano

**Requisitos Funcionales:**
- RF-1. Punto de entrada único (`agent_service.handle_message()`) que se invoca después del pre-filtro de US-031 (comandos exactos y crisis ya descartados)
- RF-2. Construye el `CompletionRequest` con: system prompt (US-010), contexto del usuario relevante (perfil resumido, últimas interacciones), el mensaje actual, y `tools=get_tools_for_user(...)` (US-159)
- RF-3. Llama a `AIRouter.complete()` con tier SMART
- RF-4. Si `stop_reason == TOOL_USE`: ejecuta cada `ToolCall` contra su handler en `TOOL_REGISTRY`, recolecta `ToolResult`s, y vuelve a llamar al modelo con esos resultados agregados a la conversación (multi-turno interno)
- RF-5. Límite de iteraciones del loop por turno (máx. 4 idas y vueltas modelo↔tools) — si se excede, corta y responde con un mensaje genérico + log de alerta (posible loop patológico o prompt injection)
- RF-6. Si `stop_reason == END_TURN`: envía la respuesta de texto al usuario vía `MessagingChannel` (US-015/US-017)
- RF-7. Si una tool retorna error, el error se comunica al modelo como `ToolResult(is_error=True, ...)` para que redacte una respuesta apropiada al usuario — nunca se expone el stack trace ni detalle técnico al usuario
- RF-8. Todo el intercambio (mensaje entrante, tool calls, tool results, respuesta final) se persiste en `historial_conversacion` para auditoría y para dar contexto a futuros turnos

**Requisitos No Funcionales:**
- RNF-1. Latencia objetivo: turno sin tools < 3s, turno con 1-2 tools < 6s (WhatsApp requiere respuesta percibida como "conversación", no como carga de página)
- RNF-2. El loop debe ser resiliente a que `AIRouter.complete()` falle a mitad de una secuencia de tools ya ejecutadas — las tools ya ejecutadas (con efectos de escritura) no se revierten automáticamente; se registra el estado parcial y se informa al usuario de forma honesta ("registré tu comida, pero tuve un problema armando la respuesta — aquí está el resumen: ...")
- RNF-3. Ninguna tool sensible (`registrar_peso`, `derivar_a_profesional`, `marcar_crisis`) se ejecuta dos veces por el mismo `tool_call.id` (idempotencia) — protege contra reintentos duplicados del loop

**Flujos:**
```
Mensaje pasa el pre-filtro (US-031), no es comando ni crisis
  ↓
agent_service.handle_message(user_id, mensaje)
  ↓
request = build_request(user, mensaje, tools=get_tools_for_user(user))
  ↓
response = ai_router.complete(request, tier=SMART)
  ↓
mientras response.stop_reason == TOOL_USE y iteraciones < 4:
    resultados = [ejecutar_tool(tc) for tc in response.tool_calls]
    request = agregar_resultados(request, resultados)
    response = ai_router.complete(request, tier=SMART)
  ↓
si iteraciones == 4: cortar, responder genérico, loguear alerta
si no: enviar response.content al usuario vía MessagingChannel
  ↓
persistir turno completo en historial_conversacion
```

**Criterios de Aceptación:**
- [ ] CA-1: "me comí 3 tacos y ya no quiero mensajes en la tarde" invoca `registrar_comida` Y `ajustar_horario_mensajes` en el mismo turno, y la respuesta final confirma ambas acciones
- [ ] CA-2: Un mensaje sin necesidad de tools responde en un solo round-trip (sin ida y vuelta de tools)
- [ ] CA-3: Tool que falla no rompe el turno — el usuario recibe una respuesta honesta, no un error crudo
- [ ] CA-4: Loop se corta a las 4 iteraciones con log de alerta si el modelo insiste en llamar tools indefinidamente
- [ ] CA-5: Reintento de un `tool_call.id` ya ejecutado (por reintento de red del provider) no duplica el registro en DB
- [ ] CA-6: Todo el turno (entrante, tool calls, resultados, saliente) queda trazable en `historial_conversacion`
- [ ] CA-7: Latencia p95 de un turno con 1 tool < 6 segundos en ambiente de staging

**Dependencias:**
- Requiere: US-006 y US-009 extendidas, US-159 (catálogo de tools), US-031 (pre-filtro), US-010 (prompts)
- Bloquea: prácticamente todo lo demás de EP-06/EP-07 en adelante, ya que este es el orquestador central de cada turno

**Notas técnicas:** Este es el componente más nuevo y menos probado del stack (tool-use en producción con datos de salud reales). Se recomienda un periodo de pruebas manuales intensivas (shadow mode: correr el loop y comparar contra el comportamiento esperado sin enviar la respuesta al usuario todavía) antes de exponerlo a usuarios reales — esto conecta con el punto de red-teaming conversacional ya identificado en `koach-analisis-brechas.md` (Parte 6, punto 6.5).

**Fuera de alcance:** Memoria semántica de largo plazo vía embeddings/pgvector (mencionada en ADR-006 como "futuro") — este loop usa solo el contexto explícito que se le construye en RF-2, no retrieval automático.

---

## EP-07 — Motor de Proactividad

---

### US-037: Infraestructura Celery

**Estimación:** 3 hrs | **Prioridad:** Crítica

**Como** sistema
**Quiero** ejecutar tareas programadas
**Para que** Koach pueda buscar al usuario

**Requisitos Funcionales:**
- RF-1. Celery configurado con Redis
- RF-2. Celery Beat para tareas periódicas
- RF-3. Worker separado del API
- RF-4. Reintentos con backoff
- RF-5. Dead letter queue para fallos persistentes

**Criterios de Aceptación:**
- [ ] CA-1: Tarea programada se ejecuta a la hora correcta
- [ ] CA-2: Fallo dispara reintento (3 intentos)
- [ ] CA-3: Worker se recupera tras reinicio sin perder tareas
- [ ] CA-4: Tareas fallidas persistentes van a DLQ

---

### US-038: Scheduler de mensajes proactivos

**Estimación:** 4 hrs | **Prioridad:** Crítica

**Como** agente
**Quiero** enviar mensajes en los horarios de cada usuario
**Para que** el acompañamiento sea real

**Requisitos Funcionales:**
- RF-1. Beat corre cada 15 minutos
- RF-2. Consulta usuarios con mensajes pendientes en esa ventana
- RF-3. Respeta timezone del usuario
- RF-4. Respeta modo silencio
- RF-5. Distribución con jitter aleatorio (evitar picos)

**Algoritmo:**
```python
@celery.task
def check_scheduled_messages():
    ahora = datetime.now(UTC)
    ventana_fin = ahora + timedelta(minutes=15)

    usuarios = get_usuarios_con_mensaje_en_ventana(ahora, ventana_fin)

    for usuario in usuarios:
        if usuario.modo_silencio_activo:
            continue

        # Jitter para distribuir carga
        delay = random.randint(0, 600)
        send_proactive_message.apply_async(
            args=[usuario.id, tipo_mensaje],
            countdown=delay,
        )
```

**Criterios de Aceptación:**
- [ ] CA-1: Usuario con "buenos días 7:00" recibe entre 7:00-7:10
- [ ] CA-2: Timezone diferente recibe a su hora local
- [ ] CA-3: Modo silencio activo no recibe nada
- [ ] CA-4: 500 usuarios a la misma hora no saturan la API

---

### US-039: Agenda diaria configurable

**Estimación:** 3 hrs | **Prioridad:** Alta

**Como** usuario
**Quiero** configurar cuándo me escribe Koach
**Para que** no me moleste en mal momento

**Requisitos Funcionales:**
- RF-1. Horarios default según plan maestro
- RF-2. Comando para ajustar: "cambia mi hora de buenos días a las 6"
- RF-3. Validación de horarios lógicos
- RF-4. Guardar en `configuracion_agente.horarios`

**Estructura JSONB:**
```json
{
  "buenos_dias": "07:00",
  "checkin_desayuno": "09:30",
  "colacion_am": "11:00",
  "sugerencia_comida": "13:30",
  "hidratacion": "15:30",
  "colacion_pm": "16:00",
  "checkin_ejercicio": "18:30",
  "checkin_cena": "20:30",
  "resumen_dia": "21:30",
  "recordatorio_dormir": "22:30"
}
```

**Criterios de Aceptación:**
- [ ] CA-1: Usuario puede cambiar cualquier horario por chat
- [ ] CA-2: Horario inválido (25:00) se rechaza con mensaje claro
- [ ] CA-3: Cambio aplica desde el día siguiente

---

### US-040: Modo silencio

**Estimación:** 2 hrs | **Prioridad:** Media

**Como** usuario
**Quiero** pausar los mensajes
**Para que** no me molesten en vacaciones

**Requisitos Funcionales:**
- RF-1. Comando `PAUSA` con duración
- RF-2. Opciones: hoy, 3 días, 1 semana, indefinido
- RF-3. Comando `REANUDAR` para volver
- RF-4. Mensaje de despedida y bienvenida

**Criterios de Aceptación:**
- [ ] CA-1: `PAUSA` pregunta duración con botones
- [ ] CA-2: Durante pausa no llega ningún mensaje proactivo
- [ ] CA-3: Al expirar, mensaje de bienvenida de vuelta
- [ ] CA-4: Usuario puede escribir en cualquier momento (bidireccional)

---

### US-041: Mensajes de reenganche

**Estimación:** 2 hrs | **Prioridad:** Alta

**Como** agente
**Quiero** contactar a usuarios inactivos
**Para que** no se pierdan

**Requisitos Funcionales:**
- RF-1. Detecta usuarios sin interacción por 3 días
- RF-2. Mensaje empático, no culpabilizante
- RF-3. Ofrece opciones: continuar, pausar, ajustar frecuencia
- RF-4. Escalamiento: 3 días → 7 días → 14 días (última vez)
- RF-5. Tras 21 días sin respuesta, pausa automática

**Criterios de Aceptación:**
- [ ] CA-1: Usuario inactivo 3 días recibe reenganche
- [ ] CA-2: Mensaje NO regaña ni culpabiliza
- [ ] CA-3: Tras 21 días, pausa automática (no spam)

---

## EP-08 — Rachas y Resúmenes

---

### US-042: Cálculo de rachas

**Estimación:** 3 hrs | **Prioridad:** Alta

**Como** usuario
**Quiero** ver mi racha de días cumplidos
**Para que** me motive a seguir

**Requisitos Funcionales:**
- RF-1. Job nocturno (23:55 hora local) evalúa el día
- RF-2. Criterio de "día cumplido" configurable
- RF-3. Rachas por tipo: general, nutrición, ejercicio, hidratación
- RF-4. Registro de mejor racha histórica
- RF-5. Lógica pura en dominio (testeable)

**Criterio de día cumplido (general):**
```python
def dia_cumplido(registros: RegistrosDia) -> bool:
    return (
        registros.comidas_registradas >= 2
        and (registros.ejercicio_completado or registros.es_dia_descanso)
        and registros.vasos_agua >= registros.meta_agua * 0.7
    )
```

**Criterios de Aceptación:**
- [ ] CA-1: Día cumplido incrementa racha
- [ ] CA-2: Día no cumplido resetea a 0
- [ ] CA-3: Día de descanso programado no rompe racha
- [ ] CA-4: Mejor racha se actualiza correctamente
- [ ] CA-5: Cálculo respeta timezone del usuario

---

### US-043: Resumen nocturno

**Estimación:** 2 hrs | **Prioridad:** Alta

**Como** usuario
**Quiero** un resumen de mi día
**Para que** vea mi progreso

**Requisitos Funcionales:**
- RF-1. Enviado a hora configurada (default 21:30)
- RF-2. Incluye: % calorías, agua, ejercicio, racha
- RF-3. Mensaje motivacional según desempeño y tono
- RF-4. Formato compacto (< 8 líneas)

**Ejemplo:**
```
Resumen de hoy, Jaziel 📊

🍽️ Nutrición: 1,840 / 2,000 kcal (92%)
💧 Agua: 6 / 8 vasos
💪 Ejercicio: ✅ Completado

Racha: 12 días 🔥

Vas muy bien. Mañana toca piernas 💪
```

**Criterios de Aceptación:**
- [ ] CA-1: Datos coinciden con registros del día
- [ ] CA-2: Mensaje motivacional varía (no repetitivo)
- [ ] CA-3: Tono respeta preferencia del usuario

---

### US-044: Celebración de hitos

**Estimación:** 2 hrs | **Prioridad:** Media

**Como** usuario
**Quiero** que celebren mis logros
**Para que** me sienta reconocido

**Requisitos Funcionales:**
- RF-1. Hitos de racha: 3, 7, 14, 30, 60, 90, 180, 365 días
- RF-2. Mensaje especial en cada hito
- RF-3. Registro en tabla `logros`
- RF-4. Mensaje incluye dato interesante (ej: "7 días ya es un hábito")

**Criterios de Aceptación:**
- [ ] CA-1: Al llegar a 7 días, mensaje especial
- [ ] CA-2: Logro registrado en DB sin duplicados
- [ ] CA-3: Mensajes de hito son distintos entre sí

---

# 13. FASE 2 — NUTRICIÓN COMPLETA

## EP-09 — Alacena Inteligente

### US-045: Registro de alacena por NL
### US-046: Actualización incremental de alacena
### US-047: Consulta de alacena
### US-048: Sugerencias basadas en alacena

## EP-10 — Plan Semanal

### US-049: Generación automática dominical
### US-050: Ajuste de plan por eventos
### US-051: Sustitución de comidas
### US-052: Vista de plan semanal en WhatsApp

## EP-11 — Lista de Compras

### US-053: Cálculo de faltantes
### US-054: Generación de lista agrupada
### US-055: Envío dominical automático

## EP-12 — Modo "Comí Fuera"

### US-056: Detección de comida fuera
### US-057: Estimación de platillos de fonda/taquería
### US-058: Ajuste del resto del día

## EP-13 — Audio y Voz

### US-059: Interface TranscriptionProvider
### US-060: Whisper API provider
### US-061: Pipeline audio → texto → intención

## EP-14 — Biblioteca de Ejercicios

### US-062: Modelo y seed de ejercicios
### US-063: Detección de duda sobre ejercicio
### US-064: Envío de video explicativo
### US-065: Sustitución por equipamiento

## EP-15 — Aprendizaje de Patrones

### US-066: Detección de patrones temporales
### US-067: Registro de preferencias por corrección
### US-068: Aplicación de patrones en sugerencias

---

# 14. FASE 3 — APP Y DASHBOARD

## EP-16 — Dashboard Web
### US-069 a US-073

## EP-17 — App Móvil
### US-074 a US-079

## EP-18 — Reportes PDF
### US-080 a US-083

## EP-19 — Modo Gym Avanzado
### US-084 a US-087

## EP-20 — Notificaciones Push
### US-088 a US-090

---

# 15. FASE 4 — CHAT NATIVO Y MONETIZACIÓN

## EP-21 — Chat Nativo en App
### US-091 a US-095

## EP-22 — Pagos y Suscripciones
### US-096 a US-101

## EP-23 — Facturación CFDI
### US-102 a US-104

## EP-24 — Sistema de Referidos
### US-105 a US-107

## EP-25 — Analytics
### US-108 a US-111

---

# 16. FASE 5 — PERFILES ESPECIALIZADOS

## EP-26 — Sistema de Perfiles

### US-112: Modelo de perfiles configurables

**Como** sistema
**Quiero** perfiles que modifiquen comportamiento
**Para que** podamos atender nichos sin fragmentar el producto

**Requisitos Funcionales:**
- RF-1. Tabla `configuraciones_perfil` con reglas por perfil
- RF-2. Usuario puede tener múltiples perfiles activos
- RF-3. Prompts se componen según perfiles activos
- RF-4. Restricciones se acumulan (la más restrictiva gana)

**Modelo:**
```sql
CREATE TABLE configuraciones_perfil (
    perfil_id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion TEXT,
    tono_default VARCHAR(20),
    prompt_adicional_path VARCHAR(200),
    restricciones_nutricionales JSONB,
    restricciones_ejercicio JSONB,
    protocolos_medicos JSONB,
    mensajes_adicionales JSONB,
    activo BOOLEAN DEFAULT TRUE
);

ALTER TABLE perfiles
ADD COLUMN perfiles_activos JSONB DEFAULT '["adulto_ocupado"]';
```

### US-113: Detección de perfil en onboarding
### US-114: Composición de prompts por perfil
### US-115: Cambio de perfil por el usuario

## EP-27 — Perfil Post-parto
### US-116 a US-119

## EP-28 — Perfil Adulto Mayor
### US-120 a US-123

## EP-29 — Perfil Diabetes T2
### US-124 a US-128

---

## EP-30 — MIGRACIÓN A IA LOCAL

Esta épica es la razón por la que diseñamos la abstracción desde el día 1.

---

### US-129: Evaluación de modelos locales candidatos

**Estimación:** 6 hrs | **Prioridad:** Media

**Como** empresa
**Quiero** evaluar qué modelos locales sirven para cada tier
**Para que** la migración mantenga calidad

**Requisitos Funcionales:**
- RF-1. Suite de evaluación con casos reales de Koach
- RF-2. Métricas: calidad de respuesta, latencia, uso de VRAM
- RF-3. Comparación contra baseline (Claude/Gemini)
- RF-4. Documentar resultados en ADR

**Candidatos a evaluar:**

| Tier | Modelo | VRAM | Notas |
|------|--------|------|-------|
| FAST | Llama 3.2 3B | 4 GB | Clasificación, extracción |
| FAST | Qwen 2.5 3B | 4 GB | Buen español |
| FAST | Phi-4 mini | 6 GB | Eficiente |
| SMART | Llama 3.3 70B | 48 GB | Requiere GPU grande |
| SMART | Qwen 2.5 32B | 24 GB | Balance calidad/tamaño |
| SMART | Mistral Small | 24 GB | Bueno en español |
| AUDIO | faster-whisper large-v3 | 6 GB | Transcripción |
| VISION | Qwen2-VL 7B | 16 GB | Análisis de comida |

**Casos de prueba:**
1. Clasificar 100 mensajes reales de usuarios
2. Parsear 50 descripciones de comidas mexicanas
3. Generar 20 planes nutricionales
4. Detectar 30 casos de crisis (incluyendo falsos positivos)
5. Responder 40 preguntas de salud

**Criterios de Aceptación:**
- [ ] CA-1: Reporte comparativo documentado
- [ ] CA-2: Modelo FAST local alcanza > 90% de accuracy vs Gemini
- [ ] CA-3: Modelo SMART local alcanza > 85% de calidad subjetiva
- [ ] CA-4: Detección de crisis local NO tiene falsos negativos

**⚠️ Nota crítica:** La detección de crisis debe mantenerse en el modelo más capaz disponible, incluso si eso significa seguir usando API. La seguridad del usuario es prioritaria sobre el ahorro de costos.

---

### US-130: Provider Ollama

**Estimación:** 4 hrs | **Prioridad:** Media

**Como** sistema
**Quiero** usar modelos locales vía Ollama
**Para que** reduzcamos costos de API

**Requisitos Funcionales:**
- RF-1. `OllamaProvider` implementa `LLMProvider`
- RF-2. Configuración de modelo por tier
- RF-3. Health check verifica que el modelo esté cargado
- RF-4. Manejo de cold start (primera petición lenta)
- RF-5. Streaming soportado

**Contratos:**
```python
class OllamaProvider(LLMProvider):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_map: dict[ModelTier, str] | None = None,
        timeout: int = 120,  # Local puede ser más lento
    ):
        ...
```

**Criterios de Aceptación:**
- [ ] CA-1: `complete()` funciona con Llama 3.2 local
- [ ] CA-2: Cambiar `AI_FAST_PROVIDER=ollama` funciona sin más cambios
- [ ] CA-3: Ollama caído dispara fallback a API
- [ ] CA-4: Tests pasan igual con provider local o API

---

### US-131: Provider vLLM (producción)

**Estimación:** 5 hrs | **Prioridad:** Baja

**Como** sistema
**Quiero** servir modelos locales con alto throughput
**Para que** escalemos sin costos de API

**Requisitos Funcionales:**
- RF-1. `VLLMProvider` con API compatible OpenAI
- RF-2. Batching automático de requests
- RF-3. Configuración de tensor parallelism
- RF-4. Métricas de throughput

**Criterios de Aceptación:**
- [ ] CA-1: Maneja 50 requests concurrentes
- [ ] CA-2: Latencia p95 < 3 segundos para tier FAST
- [ ] CA-3: Compatible con la misma interface

---

### US-132: Whisper local

**Estimación:** 3 hrs | **Prioridad:** Media

**Como** sistema
**Quiero** transcribir audio localmente
**Para que** reduzcamos costos y mejoremos privacidad

**Requisitos Funcionales:**
- RF-1. `LocalWhisperProvider` con faster-whisper
- RF-2. Modelo large-v3 para español
- RF-3. Detección automática de idioma
- RF-4. Procesamiento asíncrono

**Criterios de Aceptación:**
- [ ] CA-1: Transcribe audio de 30s en < 5 segundos
- [ ] CA-2: Accuracy comparable a Whisper API en español mexicano
- [ ] CA-3: Maneja audio con ruido de fondo

---

### US-133: Estrategia híbrida y migración gradual

**Estimación:** 6 hrs | **Prioridad:** Media

**Como** empresa
**Quiero** migrar gradualmente a local
**Para que** no arriesguemos calidad de golpe

**Requisitos Funcionales:**
- RF-1. Configuración por tarea, no solo por tier
- RF-2. Feature flags para migración progresiva
- RF-3. Shadow mode: ejecutar ambos y comparar
- RF-4. Rollback instantáneo si degrada calidad
- RF-5. Dashboard de comparación de calidad

**Estrategia de migración sugerida:**

```
Etapa 1 (Mes 12): Clasificación de intención → local
  Riesgo: bajo. Volumen: alto. Ahorro: significativo.

Etapa 2 (Mes 14): Transcripción de audio → local
  Riesgo: bajo. Ahorro: moderado.

Etapa 3 (Mes 16): Parseo de comidas → local
  Riesgo: medio. Volumen: alto.

Etapa 4 (Mes 18): Generación de planes → local
  Riesgo: medio-alto. Requiere modelo grande.

NUNCA migrar:
  - Detección de crisis (siempre el mejor modelo disponible)
  - Protocolos médicos sensibles
```

**Configuración por tarea:**
```bash
# Migración granular
AI_TASK_INTENT_CLASSIFICATION=ollama
AI_TASK_MEAL_PARSING=ollama
AI_TASK_PLAN_GENERATION=anthropic   # Sigue en API
AI_TASK_CRISIS_DETECTION=anthropic  # NUNCA local
AI_TASK_TRANSCRIPTION=local_whisper
```

**Criterios de Aceptación:**
- [ ] CA-1: Migrar una tarea no afecta las demás
- [ ] CA-2: Shadow mode registra diferencias sin afectar usuario
- [ ] CA-3: Rollback por variable de entorno en < 1 minuto
- [ ] CA-4: Detección de crisis nunca puede configurarse como local

---

## RESUMEN DE INVERSIÓN EN INFRAESTRUCTURA LOCAL (futuro)

Para cuando llegues a la Fase 5:

| Opción | Hardware | Costo | Capacidad |
|--------|----------|-------|-----------|
| Mínima | RTX 4060 Ti 16GB | ~$10,000 MXN | Modelos 7B-13B |
| Recomendada | RTX 4090 24GB | ~$40,000 MXN | Modelos hasta 32B |
| Óptima | 2× RTX 4090 | ~$80,000 MXN | Modelos 70B cuantizados |
| Cloud GPU | RunPod A100 | ~$1.50 USD/hr | Bajo demanda |

**Punto de equilibrio:** Cuando el gasto mensual en APIs supere ~$3,000 MXN, evaluar hardware propio.

Con tu ASUS ROG Flow Z13 (RTX 3050 Ti 4GB) puedes correr modelos 3B cuantizados para desarrollo y pruebas, pero no producción.

---

# ANEXO A — ORDEN DE EJECUCIÓN RECOMENDADO

## Semana 1-3 (30 hrs)
```
US-000 → US-001 → US-002 → US-003 → US-004 → US-005
US-006 → US-007 → US-008 → US-009 → US-010
US-011 → US-012 → US-013 → US-014
```

## Semana 4 — Vacaciones (40 hrs)
```
Día 1: US-015 → US-016 → US-017
Día 2: US-020 → US-021 → US-022 → US-023
Día 3: US-026 → US-027 → US-028
Día 4: US-031 → US-032 → US-033 → US-034
Día 5: US-037 → US-038 → deploy y pruebas
```

## Semana 5-8 (40 hrs)
```
US-018 → US-019 → US-024 → US-025
US-029 → US-030 → US-035 → US-036
US-039 → US-040 → US-041
US-042 → US-043 → US-044
```

---

# ANEXO B — PLANTILLA DE CLAUDE.md

```markdown
# Koach — Instrucciones para Claude Code

## Contexto del proyecto
Koach es un agente de salud proactivo por WhatsApp para mexicanos.
Documentación completa en `docs/plan-maestro.md`.
Plan técnico en `docs/plan-desarrollo-sdd.md`.

## Reglas NO NEGOCIABLES

### 1. Abstracción de IA
NUNCA importes `anthropic`, `google.generativeai` u otro SDK de IA
fuera de `app/ai/providers/`. Todo acceso pasa por `app/ai/`.

❌ MAL:
```python
# app/services/meal_service.py
import anthropic
client = anthropic.Anthropic()
```

✅ BIEN:
```python
# app/services/meal_service.py
from app.ai.tasks.meal_parsing import parse_meal_description
```

### 2. Prompts en archivos
NUNCA hardcodees prompts en Python. Van en `app/ai/prompts/*.yaml`.

### 3. Seguridad
- Secretos solo vía `app/core/config.py`
- RLS obligatorio en tablas nuevas
- Datos de salud nunca en logs

### 4. Detección de crisis
La detección de crisis emocional tiene prioridad sobre TODO.
Nunca la optimices por costo. Nunca la muevas a modelos menos capaces.

### 5. Idiomas
- Código, comentarios, docstrings: inglés
- Mensajes al usuario, prompts: español mexicano

### 6. Calidad
- Type hints obligatorios
- Tests para lógica de dominio
- `ruff check` y `mypy app` deben pasar

## Antes de implementar una US
1. Lee `docs/specs/EP-XX/US-YYY.md`
2. Verifica dependencias
3. Propón plan antes de escribir código
4. Confirma conmigo antes de crear migraciones

## Comandos
```bash
pytest -v                      # Tests
ruff check . && mypy app       # Lint
alembic revision --autogenerate -m "msg"
uvicorn app.main:app --reload  # Dev server
celery -A app.workers.celery_app worker -l info
celery -A app.workers.celery_app beat -l info
```

## Estructura de commits
```
feat(scope): descripción
fix(scope): descripción
docs(scope): descripción
refactor(scope): descripción
test(scope): descripción
```
```

---

*Koach — Plan de Desarrollo SDD v1.0*
*Mayo 2026*
