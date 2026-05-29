# CHANGELOG — Koach
> Actualizado automáticamente por Claude Code al completar cada US.
> Formato: US completadas en orden cronológico inverso (más reciente arriba).

---

## Estado del proyecto

| Métrica | Valor |
|---------|-------|
| **Fase actual** | Setup — Semana 1 |
| **US completadas** | 3 / 8 (MVP) |
| **Última actualización** | 2026-05-29 |
| **Deploy backend** | ⏳ Pendiente |
| **Deploy frontend** | ⏳ Pendiente |
| **Usuarios beta** | 0 |

---

## US en progreso

*Ninguna en progreso actualmente.*

---

## US completadas

## US-002 — Detección de usuario y onboarding conversacional | 2026-05-29

**Qué se implementó:**
- `handle_message` implementado: detecta usuario existente (→ saludo) o nuevo (→ onboarding)
- Máquina de estados de 7 pasos con persistencia en `onboarding_estado` (Supabase)
- Consentimiento LFPDPPP antes de cualquier pregunta de datos personales
- Validación por paso: edad mínima 13 años (CE-02), peso fuera de rango con confirmación (CE-03)
- FA-04: máximo 3 intentos por paso antes de sugerir "reiniciar"
- Comando "reiniciar" disponible en cualquier momento del flujo
- Creación de registros en `usuarios`, `perfiles` y `consentimientos` al completar
- Envío de mensajes vía `whatsapp_sender.send_message()` con httpx.AsyncClient
- BackgroundTasks de FastAPI: `handle_message` es async para no bloquear el endpoint
- Todos los mensajes centralizados en `es_mx.py` (CA-09)

**Archivos creados:**
- `backend/scripts/init_db_us002.sql` — DDL de las 4 tablas (referencia y reproducibilidad)
- `backend/app/db/__init__.py` — paquete db
- `backend/app/db/supabase.py` — singleton del cliente Supabase
- `backend/app/messages/__init__.py` — paquete messages
- `backend/app/messages/es_mx.py` — todos los mensajes del bot en español mexicano
- `backend/app/services/whatsapp_sender.py` — send_message() con httpx.AsyncClient
- `backend/app/services/onboarding.py` — máquina de estados + validación + helpers de DB
- `backend/tests/pytest.ini` — asyncio_mode = auto para tests async sin decoradores
- `backend/tests/test_onboarding.py` — 21 tests (CA-01→CA-08 + unidades de validación)

**Archivos modificados:**
- `backend/app/core/config.py` — agregado `whatsapp_phone_number_id: str` (requerido)
- `backend/.env.example` — agregado `WHATSAPP_PHONE_NUMBER_ID`
- `backend/requirements.txt` — agregado `httpx==0.28.1`
- `backend/app/services/whatsapp.py` — implementado `handle_message` (de stub a async funcional)
- `backend/tests/conftest.py` — agregada variable de entorno `WHATSAPP_PHONE_NUMBER_ID`

**Tests agregados:**
- `backend/tests/test_onboarding.py` — 21 tests que cubren CA-01 a CA-08, CE-02, FA-04 y unidades de `_validate_answer`

**Deuda técnica registrada:**
- El disparo de US-003 al completar onboarding es solo un `logger.info` por ahora — pendiente conectar en US-003

---

## US-001 — Webhook WhatsApp: recibir y verificar mensajes | 2026-05-29

**Qué se implementó:**
- Endpoint GET /webhook con verificación challenge-response de Meta (hub.mode, hub.verify_token, hub.challenge vía Query aliases)
- Endpoint POST /webhook que retorna HTTP 200 inmediatamente y despacha handle_message como BackgroundTask
- Parseo robusto del payload de WhatsApp Cloud API con Pydantic v2
- Logging de cada mensaje recibido (phone, msg_id, texto)
- Manejo de payloads malformados y mensajes no-texto sin romper el servidor
- Router modular en app/api/ integrado limpiamente en main.py

**Archivos creados:**
- `backend/app/api/__init__.py` — paquete api
- `backend/app/api/api.py` — router principal que agrupa endpoints
- `backend/app/api/endpoints/__init__.py` — paquete endpoints
- `backend/app/api/endpoints/webhook.py` — endpoints GET y POST /webhook
- `backend/app/schemas/__init__.py` — paquete schemas
- `backend/app/schemas/whatsapp.py` — modelos Pydantic del payload WhatsApp
- `backend/app/services/__init__.py` — paquete services
- `backend/app/services/whatsapp.py` — función handle_message (vacía, US-002)
- `backend/tests/__init__.py` — paquete tests
- `backend/tests/conftest.py` — fixture TestClient con token de prueba
- `backend/tests/test_webhook.py` — 6 tests (CA-01 a CA-05 + body inválido)

**Archivos modificados:**
- `backend/app/core/config.py` — agregado whatsapp_verify_token: str (requerido), migrado a SettingsConfigDict
- `backend/.env.example` — agregado WHATSAPP_VERIFY_TOKEN
- `backend/app/main.py` — incluido api_router con los endpoints del webhook

**Tests agregados:**
- `backend/tests/test_webhook.py` — GET token válido → challenge, GET token inválido → 403, POST payload válido → 200, POST mensaje audio → 200, POST payload malformado → 200, POST body no-JSON → 200

**Deuda técnica registrada:**
- Ninguna

---

## US-000 — Estructura base del proyecto | 2026-05-28

**Qué se implementó:**
- Estructura de carpetas del backend (FastAPI) siguiendo la arquitectura definida en CLAUDE.md
- Endpoint GET /health funcional que retorna `{"status": "ok", "project": "koach"}`
- Configuración de Settings con pydantic-settings (carga desde .env)
- Dependencias base del proyecto en requirements.txt
- Variables de entorno documentadas en .env.example
- Carpeta docs/specs/ lista para recibir specs de User Stories
- .gitignore para Python + Next.js (protege .env de commits accidentales)

**Archivos creados:**
- `backend/app/__init__.py` — hace de `app` un paquete Python importable
- `backend/app/core/__init__.py` — hace de `app.core` un paquete Python importable
- `backend/app/main.py` — FastAPI app con endpoint /health
- `backend/app/core/config.py` — Settings con pydantic-settings
- `backend/requirements.txt` — dependencias de producción: fastapi, uvicorn, python-dotenv, pydantic-settings, anthropic, supabase
- `backend/requirements-dev.txt` — dependencias de testing: pytest, httpx, pytest-asyncio
- `backend/.env.example` — plantilla de variables de entorno
- `docs/specs/.gitkeep` — carpeta de specs versionada
- `.gitignore` — exclusiones Python + Node + OS

**Archivos modificados:**
- `CHANGELOG.md` — actualizado con US-000

**Tests agregados:**
- Ninguno (US de scaffolding sin lógica de negocio)

**Deuda técnica registrada:**
- Ninguna

---

## Decisiones técnicas registradas

| ADR | Decisión | Fecha |
|-----|----------|-------|
| — | — | — |

---

## Deuda técnica acumulada

*Sin deuda técnica registrada aún.*

---

## Historial de versiones

### v0.1.0 — Setup inicial (Mayo 2026)
- Estructura de proyecto creada
- Flujo SDD definido y documentado
- CLAUDE.md y GEMINI.md configurados
- CHANGELOG inicializado

---

*Este archivo es mantenido por Claude Code.*
*No editar manualmente — puede causar inconsistencias.*
*Para agregar notas manuales, usar la sección "Decisiones técnicas registradas".*
