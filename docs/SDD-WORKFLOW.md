# SDD — Spec-Driven Development
## Flujo de trabajo con agentes IA duales
> Koach Project — Jaziel Anguiano (CTO)
> Versión 1.0 — Mayo 2026

---

## ¿Qué es SDD?

Spec-Driven Development es una metodología donde **ninguna línea de código se escribe sin una especificación previa aprobada**. Cada funcionalidad pasa por un ciclo estructurado antes de implementarse, usando agentes IA especializados en cada etapa.

El resultado: menos retrabajo, decisiones documentadas, código más predecible y un historial trazable de por qué se construyó cada cosa.

---

## Herramientas del stack SDD

| Herramienta | Rol en SDD | Cuándo se usa |
|-------------|-----------|---------------|
| **Claude Code** (VS Code extension) | Implementador | Etapas 3 — escritura de código y tests |
| **Gemini** (Antigravity IDE) | Arquitecto / Revisor | Etapas 2 y 4 — planificación y revisión |
| **GitHub Projects** | Tablero de tareas | Todo el ciclo |
| **GitHub Issues** | Tracking por US | Todo el ciclo |
| **`/docs/specs/`** | Repositorio de specs | Etapas 1 y 2 |

---

## El ciclo completo

```
SPEC → PLAN → TASKS → IMPLEMENT → REVIEW → COMMIT
 (tú)  (Gemini) (Claude)  (Claude)   (Gemini)   (tú)
```

---

## ETAPA 1 — SPEC (Tú)

### ¿Qué es?
Un documento en Markdown que define **qué** debe hacer una funcionalidad, sin decir **cómo**. Vive en `/docs/specs/`.

### Cuándo está lista una spec
- Puedes explicarle a alguien qué hace sin mostrarle código
- Tiene criterios de aceptación verificables
- Incluye casos de error y bordes

### Plantilla estándar de spec

```markdown
# US-[NNN] — [Nombre de la funcionalidad]

## Contexto
[Por qué existe esta funcionalidad. Qué problema resuelve. 
Cómo encaja con el resto del sistema.]

## Descripción
Como [tipo de usuario], quiero [acción], para [beneficio].

## Requisitos funcionales
- RF-01: [Requisito concreto y verificable]
- RF-02: [Requisito concreto y verificable]
- RF-03: ...

## Requisitos no funcionales
- RNF-01: [Performance, seguridad, escalabilidad, etc.]
- RNF-02: ...

## Flujo principal
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

## Flujos alternativos
- **FA-01 — [Nombre]:** [Qué pasa cuando X falla o es diferente]
- **FA-02 — [Nombre]:** ...

## Casos de error
- **CE-01:** [Qué input rompe esto y cómo se maneja]
- **CE-02:** ...

## Criterios de aceptación
- [ ] CA-01: [Condición verificable y concreta]
- [ ] CA-02: [Condición verificable y concreta]
- [ ] CA-03: ...

## Decisiones técnicas previas
[Restricciones conocidas, decisiones ya tomadas que esta spec debe respetar]

## Fuera de scope
- [Qué NO hace esta US intencionalmente]
- [Qué se deja para una US futura]

## Referencias
- Plan maestro: sección [X]
- US relacionadas: US-[NNN], US-[NNN]
```

### Nombre del archivo
```
docs/specs/[NNN]-[nombre-con-guiones].md
```
Ejemplos:
- `001-onboarding-whatsapp.md`
- `002-conexion-whatsapp-api.md`
- `015-registro-comidas-lenguaje-natural.md`

---

## ETAPA 2 — PLAN (Gemini en Antigravity)

### ¿Qué hace Gemini aquí?
Lee la spec + el codebase actual y propone **cómo** construirlo: archivos a crear, archivos a modificar, dependencias, riesgos, orden de implementación.

### Prompt estándar para Gemini

```
Actúa como arquitecto de software senior.

Te comparto la spec de la siguiente US:

[PEGAR CONTENIDO COMPLETO DE LA SPEC]

Considerando el codebase actual, necesito que generes un plan de implementación que incluya:

1. ARCHIVOS A CREAR — nombre, ruta, responsabilidad de cada uno
2. ARCHIVOS A MODIFICAR — qué cambia y por qué
3. DEPENDENCIAS — librerías nuevas necesarias (si aplica)
4. ORDEN DE IMPLEMENTACIÓN — secuencia lógica de tareas
5. RIESGOS — qué puede salir mal y cómo mitigarlo
6. PREGUNTAS — si algo en la spec es ambiguo, señálalo antes de planear

No escribas código todavía. Solo el plan arquitectónico.
Sé específico con rutas y nombres de archivos.
```

### Output esperado de Gemini
Un documento de plan que guardas en:
```
docs/specs/[NNN]-[nombre]-plan.md
```

### ¿Cuándo aprobar el plan?
- Los archivos propuestos tienen sentido con la arquitectura existente
- No hay dependencias circulares ni duplicación de lógica
- Los riesgos están identificados
- Si Gemini hizo preguntas, las respondiste y le pediste replantear

---

## ETAPA 3 — TASKS + IMPLEMENT (Claude Code en VS Code)

### ¿Qué hace Claude Code aquí?
Toma el plan aprobado y lo convierte en tareas atómicas, luego implementa cada una con acceso directo a tus archivos.

### Prompt estándar para Claude Code — Desglose de tareas

```
Tengo esta spec y este plan de implementación aprobado:

SPEC:
[PEGAR SPEC]

PLAN APROBADO:
[PEGAR PLAN DE GEMINI]

Antes de escribir cualquier código, genera la lista de tareas atómicas
en orden de implementación. Cada tarea debe:
- Poder completarse en menos de 30 minutos
- Ser verificable (sé cuándo está lista)
- Tener un nombre claro

Formato:
- [ ] TASK-01: [descripción]
- [ ] TASK-02: [descripción]
...

No implementes nada todavía. Solo la lista.
```

### Prompt estándar para Claude Code — Implementar tarea

```
Implementa TASK-[NN]: [descripción]

Contexto:
- Spec: docs/specs/[NNN]-[nombre].md
- Plan: docs/specs/[NNN]-[nombre]-plan.md
- Tareas anteriores completadas: TASK-01, TASK-02, ...

Reglas:
- Solo implementa esta tarea, nada más
- Si necesitas crear un archivo nuevo, créalo
- Si modificas uno existente, muéstrame el diff
- Incluye manejo de errores
- Agrega comentarios donde la lógica no sea obvia
- Si encuentras algo que contradice la spec o el plan, detente y avísame
```

### Reglas de implementación con Claude Code

1. **Una tarea a la vez** — nunca pidas implementar 3 cosas juntas
2. **Revisa antes de continuar** — prueba cada tarea antes de pedir la siguiente
3. **Si Claude se desvía** — detente, muéstrale la spec y corrígelo
4. **Commits frecuentes** — después de cada tarea funcional, commit

---

## ETAPA 4 — REVIEW (Gemini en Antigravity)

### ¿Qué hace Gemini aquí?
Con acceso al codebase actualizado, revisa que lo implementado cumple la spec original. Es el QA arquitectónico.

### Prompt estándar para Gemini — Review

```
Acabo de implementar la US-[NNN]: [nombre].

Por favor revisa el código implementado contra esta spec:

[PEGAR SPEC ORIGINAL]

Quiero que evalúes:

1. COMPLETITUD — ¿Se cumplieron todos los criterios de aceptación?
   Marca cada CA como ✅ cumplido, ⚠️ parcial, o ❌ no cumplido.

2. CALIDAD — ¿Hay código frágil, mal manejado o que podría romper?

3. SEGURIDAD — ¿Hay inputs sin validar, datos expuestos, o riesgos?

4. CONSISTENCIA — ¿El código sigue los patrones del resto del proyecto?

5. DEUDA TÉCNICA — ¿Qué atajos se tomaron que habría que resolver después?

Sé directo y específico. Señala líneas o archivos concretos si encuentras problemas.
```

### ¿Cuándo pasar al commit?
- Todos los CA marcados como ✅
- No hay issues de seguridad sin resolver
- Los issues de calidad están documentados como deuda técnica si no se resuelven ahora

---

## ETAPA 5 — COMMIT (Tú)

### Convención de mensajes de commit

```
[tipo](US-NNN): descripción corta en presente

[cuerpo opcional: qué cambió y por qué]

[footer opcional: referencias]
```

**Tipos:**
- `feat` — nueva funcionalidad
- `fix` — corrección de bug
- `refactor` — mejora sin cambio de comportamiento
- `test` — solo tests
- `docs` — solo documentación
- `chore` — configuración, dependencias

**Ejemplos:**
```bash
feat(US-001): add WhatsApp onboarding flow with 5 initial questions

fix(US-003): correct Mifflin-St Jeor formula for female users

docs(US-002): add webhook verification spec and plan
```

### Checklist antes del commit

```
- [ ] Todas las tareas de la US completadas
- [ ] Review de Gemini aprobado (sin ❌)
- [ ] Criterios de aceptación verificados manualmente
- [ ] .env no incluido en el commit
- [ ] No hay console.log o print() de debug olvidados
- [ ] Issue en GitHub Projects movido a "Done"
```

---

## Estructura de carpetas del proyecto

```
koach/
├── docs/
│   ├── plan-maestro.md
│   ├── plan-ejecucion.md
│   ├── SDD-WORKFLOW.md          ← este archivo
│   ├── decisions/               ← ADRs (Architecture Decision Records)
│   │   └── ADR-001-fastapi-vs-django.md
│   └── specs/
│       ├── 001-onboarding-whatsapp.md
│       ├── 001-onboarding-whatsapp-plan.md
│       ├── 002-conexion-whatsapp-api.md
│       ├── 002-conexion-whatsapp-api-plan.md
│       └── ...
├── backend/
├── frontend-web/
└── .github/
    └── ISSUE_TEMPLATE/
        └── user-story.md
```

---

## Plantilla de GitHub Issue (User Story)

Guardar en `.github/ISSUE_TEMPLATE/user-story.md`:

```markdown
---
name: User Story
about: Nueva funcionalidad siguiendo flujo SDD
title: 'US-[NNN]: [nombre]'
labels: user-story
---

## Spec
Link: `docs/specs/[NNN]-[nombre].md`

## Plan
Link: `docs/specs/[NNN]-[nombre]-plan.md`

## Tareas
- [ ] TASK-01: 
- [ ] TASK-02: 
- [ ] TASK-03: 

## Review
- [ ] Review de Gemini completado
- [ ] Todos los CA aprobados

## Definition of Done
- [ ] Código implementado y funcionando
- [ ] Review arquitectónico aprobado
- [ ] Commit con convención estándar
- [ ] Issue cerrado
```

---

## Architecture Decision Records (ADR)

Cuando tomes una decisión técnica importante que afecte el proyecto a largo plazo, documéntala en `/docs/decisions/`.

### Plantilla ADR

```markdown
# ADR-[NNN] — [Título de la decisión]

**Fecha:** YYYY-MM-DD
**Estado:** Propuesta | Aprobada | Deprecada

## Contexto
[Por qué se tuvo que tomar esta decisión. Qué problema resuelve.]

## Opciones consideradas
1. [Opción A] — [pros y contras]
2. [Opción B] — [pros y contras]
3. [Opción C] — [pros y contras]

## Decisión
[Qué se eligió y por qué.]

## Consecuencias
[Qué se gana, qué se sacrifica, qué deuda técnica genera.]
```

---

## Ejemplo completo — US-001

### Spec (`docs/specs/001-onboarding-whatsapp.md`)

```markdown
# US-001 — Onboarding inicial por WhatsApp

## Contexto
Cuando un usuario escribe por primera vez al número de Koach,
debe pasar por un onboarding mínimo que capture los datos
necesarios para generar su plan del día 1. El onboarding debe
ser conversacional, no un formulario. El consentimiento LFPDPPP
debe obtenerse antes de guardar cualquier dato de salud.

## Descripción
Como nuevo usuario de Koach, quiero responder preguntas simples
por WhatsApp, para recibir mi plan personalizado desde el primer día.

## Requisitos funcionales
- RF-01: Detectar si el número es nuevo (no existe en `users`)
- RF-02: Obtener consentimiento explícito antes de preguntas de salud
- RF-03: Capturar: nombre, edad, peso, talla, género, meta, alergias
- RF-04: Una pregunta a la vez, con validación de respuesta
- RF-05: Al completar, crear registros en `users`, `perfiles`
- RF-06: Disparar US-003 (generación de plan) al terminar

## Requisitos no funcionales
- RNF-01: El estado del onboarding debe persistir si el usuario
  no termina en una sesión (puede continuar al día siguiente)
- RNF-02: Respuesta al usuario en menos de 3 segundos
- RNF-03: Manejar respuestas inesperadas con mensaje de ayuda

## Flujo principal
1. Usuario escribe cualquier mensaje al número de Koach
2. Sistema detecta número nuevo → inicia onboarding
3. Koach saluda y pide consentimiento LFPDPPP
4. Usuario acepta → Koach hace 7 preguntas una por una
5. Al completar: crear registros, disparar generación de plan
6. Koach confirma: "¡Listo! Generando tu plan..."

## Flujos alternativos
- FA-01 — Usuario rechaza consentimiento: Koach explica que no
  puede continuar sin ello. Ofrece link a aviso de privacidad.
  No guarda ningún dato.
- FA-02 — Usuario abandona a mitad: al volver, Koach retoma
  desde la última pregunta contestada.
- FA-03 — Respuesta inválida: Koach repite la pregunta con
  ejemplo de formato esperado. Máximo 3 intentos antes de
  sugerir reiniciar.

## Casos de error
- CE-01: Peso fuera de rango (< 30kg o > 300kg) → pedir confirmación
- CE-02: Edad menor de 18 → mensaje de exclusión amable, no guardar
- CE-03: Error al guardar en Supabase → mensaje de error al usuario,
  reintentar 1 vez

## Criterios de aceptación
- [ ] CA-01: Número nuevo recibe saludo y solicitud de consentimiento
- [ ] CA-02: Sin consentimiento, ningún dato se guarda en DB
- [ ] CA-03: Respuesta inválida genera mensaje de ayuda, no rompe el flujo
- [ ] CA-04: Al completar, existe registro en `users` y `perfiles`
- [ ] CA-05: Menor de 18 años no puede completar el onboarding
- [ ] CA-06: Usuario que abandona retoma desde donde dejó
- [ ] CA-07: Consentimiento queda registrado en tabla `consentimientos`

## Decisiones técnicas previas
- Stack: FastAPI + Supabase (PostgreSQL) + WhatsApp Cloud API
- Estado del onboarding guardado en tabla `onboarding_estado` con
  campo `paso_actual` y `datos_parciales` JSONB

## Fuera de scope
- Onboarding para días 2-7 (preguntas progresivas) → US-010
- Generación del plan nutricional y de ejercicio → US-003
- Envío del PDF inicial → US-008

## Referencias
- Plan maestro: Módulo 9 — Onboarding Progresivo
- US relacionadas: US-003, US-008, US-010
```

### Prompt para Gemini (Etapa 2)

```
Actúa como arquitecto de software senior.

Te comparto la spec de US-001 [pegar spec arriba].

El stack del proyecto es:
- Backend: Python 3.11 + FastAPI
- DB: Supabase (PostgreSQL)
- Mensajería: WhatsApp Cloud API (webhook POST /webhook)
- IA: Claude API (Anthropic)

Genera el plan de implementación con:
1. Archivos a crear y su responsabilidad
2. Archivos a modificar
3. Estructura de la tabla onboarding_estado si no existe
4. Orden de implementación
5. Riesgos
```

### Commit final esperado

```bash
feat(US-001): implement WhatsApp onboarding flow

- Detect new users via phone number lookup
- LFPDPPP consent flow before health data collection  
- 7-question progressive onboarding with state persistence
- Validation and error handling per spec
- Triggers US-003 on completion

Closes #1
```

---

## Resumen visual del flujo

```
┌─────────────────────────────────────────────────────────┐
│                    CICLO SDD KOACH                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. SPEC      →  Tú escribes en /docs/specs/            │
│     (30 min)     Usando plantilla estándar              │
│                                                         │
│  2. PLAN      →  Gemini (Antigravity) lee codebase      │
│     (15 min)     + spec y propone arquitectura          │
│                                                         │
│  3. TASKS     →  Claude Code (VS Code) desglosa         │
│     (10 min)     el plan en tareas atómicas             │
│                                                         │
│  4. IMPLEMENT →  Claude Code implementa                 │
│     (variable)   tarea por tarea, tú revisas            │
│                                                         │
│  5. REVIEW    →  Gemini revisa el código                │
│     (15 min)     contra los criterios de aceptación     │
│                                                         │
│  6. COMMIT    →  Tú haces commit con convención         │
│     (5 min)      y cierras el issue                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Lo que este flujo agrega a tu CV

Al terminar el proyecto, podrás decir con evidencia en GitHub:

- Implementé metodología **Spec-Driven Development** para desarrollo
  de producto con agentes IA especializados por etapa
- Usé **Claude Code** como agente implementador y **Gemini** como
  arquitecto/revisor en un flujo dual de desarrollo
- Todas las funcionalidades tienen especificación, plan, criterios
  de aceptación y revisión documentados antes de implementarse
- Reducción de retrabajo estimada: más del 40% vs desarrollo sin specs

---

*SDD-WORKFLOW.md — Koach Project*
*Jaziel Anguiano (CTO) — Mayo 2026*
*Versión 1.0*
