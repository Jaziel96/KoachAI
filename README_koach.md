# Koach 🥦
### Agente de salud proactivo por WhatsApp para mexicanos

> Estado: En desarrollo activo — MVP estimado agosto 2026

---

## ¿Qué es Koach?

Koach es un coach de nutrición y ejercicio que vive en WhatsApp. Sin app que descargar, sin formularios, sin dashboards que nadie usa. El usuario escribe como si le mandara un mensaje a un amigo y Koach entiende, recuerda y actúa.

**El problema que resuelve:** Las apps de salud tienen tasas de abandono altísimas porque piden demasiado esfuerzo. Koach apuesta por el canal donde los mexicanos ya están: WhatsApp.

---

## ¿Cómo funciona?

```
Usuario escribe por WhatsApp
        ↓
Webhook recibe el mensaje (FastAPI)
        ↓
Agente IA analiza contexto + historial (Claude API)
        ↓
Koach responde, registra o actúa
        ↓
Mensajes proactivos diarios sin que el usuario pregunte
```

**Flujo del usuario:**
1. Escribe al número de Koach por primera vez
2. Acepta el aviso de privacidad (LFPDPPP)
3. Responde 7 preguntas conversacionales: nombre, edad, peso, talla, meta, alergias
4. Recibe su plan personalizado de alimentación y ejercicio en minutos
5. Cada día: registra sus comidas en lenguaje natural, recibe su resumen y su racha

---

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11 + FastAPI |
| Base de datos | Supabase (PostgreSQL) |
| Mensajería | WhatsApp Cloud API (Meta) |
| IA principal | Claude API (Anthropic) |
| IA secundaria | Gemini Flash (Google) |
| Frontend web | Next.js + TypeScript + Tailwind CSS |
| Deploy backend | Railway |
| Deploy frontend | Vercel |
| Tareas async | Celery + Redis |

---

## Metodología de desarrollo

Este proyecto se desarrolla con **Spec-Driven Development (SDD)** y un pipeline de agentes IA duales:

```
SPEC (Jaziel) → PLAN (Gemini) → IMPLEMENT (Claude Code) → REVIEW (Gemini) → COMMIT
```

- **Claude Code** actúa como agente implementador en VS Code
- **Gemini** en Antigravity IDE actúa como arquitecto y revisor
- Cada funcionalidad tiene su especificación aprobada antes de escribir una línea de código
- La documentación se genera automáticamente al cerrar cada ciclo

Ver el flujo completo: [`docs/SDD-WORKFLOW.md`](docs/SDD-WORKFLOW.md)

---

## Estructura del proyecto

```
koach/
├── CLAUDE.md                  # Instrucciones permanentes para Claude Code
├── GEMINI.md                  # Instrucciones permanentes para Gemini
├── CHANGELOG.md               # Actualizado automáticamente por Claude Code
├── docs/
│   ├── SDD-WORKFLOW.md        # Metodología de desarrollo completa
│   ├── plan-maestro.md        # Visión completa del producto
│   ├── plan-ejecucion.md      # Plan MVP 3 meses
│   └── specs/                 # Especificaciones por US
│       ├── 001-onboarding-whatsapp.md
│       ├── 002-conexion-whatsapp-api.md
│       └── ...
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   ├── handlers/
│   │   └── models/
│   └── tests/
└── frontend-web/
```

---

## User Stories del MVP

| US | Descripción | Estado |
|----|-------------|--------|
| US-001 | Webhook WhatsApp — recibir y verificar mensajes | 🔲 Pendiente |
| US-002 | Onboarding conversacional + consentimiento LFPDPPP | 🔲 Pendiente |
| US-003 | Generación de plan inicial con Claude API | 🔲 Pendiente |
| US-004 | Flujo conversacional diario | 🔲 Pendiente |
| US-005 | Registro de comidas en lenguaje natural | 🔲 Pendiente |
| US-006 | Sistema de rachas y resumen diario | 🔲 Pendiente |
| US-007 | Mensajes proactivos matutinos | 🔲 Pendiente |
| US-008 | Generación de PDF con plan inicial | 🔲 Pendiente |

---

## Decisiones de diseño

**¿Por qué WhatsApp y no una app?**
México tiene más de 90 millones de usuarios de WhatsApp. La fricción de descargar una app es el mayor enemigo de la adopción en health tech.

**¿Por qué Claude y no solo GPT?**
Claude tiene mejor manejo de instrucciones complejas de largo plazo y menor tendencia a inventar información nutricional — crítico cuando das consejos de salud.

**¿Por qué FastAPI y no Django?**
Necesitamos responder el webhook de WhatsApp en menos de 3 segundos. FastAPI asíncrono maneja mejor la concurrencia para ese caso de uso.

---

## Cumplimiento LFPDPPP

Koach maneja datos de salud (peso, talla, condiciones, alergias). El diseño incluye desde el día uno:
- Consentimiento explícito antes de cualquier dato de salud
- Aviso de privacidad accesible vía link
- Opción de cancelación integrada en el flujo conversacional
- Datos almacenados en Supabase con RLS por usuario

---

## Autor

**Jaziel Anguiano** — [github.com/jazang](https://github.com/jazang) — Colima, México

---

*Proyecto personal en desarrollo. No afiliado a WhatsApp, Meta ni Anthropic.*
