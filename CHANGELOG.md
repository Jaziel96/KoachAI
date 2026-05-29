# CHANGELOG — Koach
> Actualizado automáticamente por Claude Code al completar cada US.
> Formato: US completadas en orden cronológico inverso (más reciente arriba).

---

## Estado del proyecto

| Métrica | Valor |
|---------|-------|
| **Fase actual** | Setup — Semana 1 |
| **US completadas** | 1 / 8 (MVP) |
| **Última actualización** | 2026-05-28 |
| **Deploy backend** | ⏳ Pendiente |
| **Deploy frontend** | ⏳ Pendiente |
| **Usuarios beta** | 0 |

---

## US en progreso

*Ninguna en progreso actualmente.*

---

## US completadas

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
- `backend/app/main.py` — FastAPI app con endpoint /health
- `backend/app/core/config.py` — Settings con pydantic-settings
- `backend/requirements.txt` — dependencias: fastapi, uvicorn, python-dotenv, pydantic-settings, anthropic, supabase
- `backend/.env.example` — plantilla de variables de entorno
- `docs/specs/.gitkeep` — carpeta de specs versionada
- `.gitignore` — exclusiones Python + Node + OS

**Archivos modificados:**
- `CHANGELOG.md` — actualizado con US-000

**Tests agregados:**
- Ninguno (US de scaffolding sin lógica de negocio)

**Deuda técnica registrada:**
- `backend/app/__init__.py` no creado — necesario para imports en proyectos más grandes; agregar en US-001 si se requiere

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
