# Koach

Agente de salud proactivo por WhatsApp para mexicanos — orientación alimentaria
(NOM-043-SSA2-2012), ejercicio y acompañamiento de hábitos, con arquitectura agéntica
de tool-use nativo sobre Claude (ver `docs/plan-desarrollo-sdd.md`, ADR-007).

## Empezar aquí

1. Lee `CLAUDE.md` — reglas técnicas no negociables del proyecto.
2. Lee `docs/plan-desarrollo-secuencial.md` — dice exactamente qué hito (M1...M12) sigue
   y con qué User Stories.
3. Lee la spec de cada US en `docs/plan-desarrollo-sdd.md` antes de implementarla.

## Setup local (backend)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # o .venv\Scripts\activate en Windows
pip install -e .
cp .env.example .env  # completar API keys y URLs de Supabase/Redis
docker-compose up -d  # levanta Redis local
alembic upgrade head
uvicorn app.main:app --reload
```

`GET /health` debe responder `200` con todas las dependencias en `up`.

## Estructura

Arquitectura hexagonal (Ports & Adapters) — ver ADR-001 en `docs/plan-desarrollo-sdd.md`.

```
backend/app/
├── domain/      # lógica pura de negocio, sin dependencias externas
├── ports/       # interfaces abstractas
├── adapters/    # implementaciones (WhatsApp, Supabase, proveedores de IA)
├── ai/          # capa de abstracción de IA (ver sección 3 del plan SDD)
├── services/    # orquestación
├── api/         # endpoints FastAPI
├── workers/     # tareas Celery (mensajes proactivos, reportes)
└── schemas/     # DTOs Pydantic
```

## Estado del proyecto

Ver `docs/plan-desarrollo-secuencial.md`, sección "RESUMEN DE HORAS" para el hito actual.
