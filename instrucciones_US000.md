# Contexto General
Crea la estructura base para el proyecto Koach siguiendo la arquitectura hexagonal.

# Requisitos Funcionales (US-000)
- RF-1. Estructura de carpetas según arquitectura hexagonal (domain, ports, adapters, etc.).
- RF-2. `CLAUDE.md` con instrucciones para Claude Code (lo añadiremos nosotros).
- RF-3. `.gitignore` completo (Python, Node, IDEs, secretos).
- RF-4. `README.md` con setup instructions.
- RF-5. Carpeta `docs/` con plan maestro y specs.

# Estructura de Carpetas Objetivo
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