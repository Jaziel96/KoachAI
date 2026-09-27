# KOACH — Plan de Desarrollo Secuencial
### Orden de ejecución por hitos, sin calendario — basado en horas
> Complemento al Plan SDD — Versión 1.2, Septiembre 2026 (v1.1 agrega hito M9 bis; v1.2 agrega el eval harness y "propone→confirma" a M9 bis, y extiende M10 para que la proactividad use el loop agéntico)
> Úsese junto con `koach-plan-desarrollo-sdd.md` (specs completas de cada US)

---

## 0. RESPUESTA A "¿PODEMOS EMPEZAR?"

**Sí, y ambos pendientes de terceros ya están resueltos o mejor de lo esperado** (ver `koach-analisis-brechas.md`, Parte 7):

| Tarea | Estado |
|-------|--------|
| Políticas de uso de IA (Anthropic/OpenAI/Google) | ✅ **Resuelto.** Anthropic excluye explícitamente "consejo de bienestar" (sueño, nutrición, ejercicio) de su categoría de Alto Riesgo — Koach queda fuera de esa categoría si se mantiene en el carril de orientación, no clínica. Refuerza el marco NOM-043 ya adoptado. |
| Verificación de negocio en Meta | ✅ **Mejor de lo esperado.** La Cloud API funciona sin verificación completa, con tope de 250 conversaciones/día — más que suficiente para el MVP y el beta inicial. La verificación se puede tramitar en paralelo sin presión de calendario, y solo es necesaria para escalar más adelante. |

Todo lo demás de este documento **se puede empezar ya**, en paralelo a que sigan las entrevistas de validación y la búsqueda de nutriólogo (ninguna de las dos bloquea escribir código, solo bloquean cobrar).

**Corrección de costos:** ver `koach-analisis-costos-actualizado.md` — el costo de WhatsApp Cloud API ya no es $0 como se asumía; es modesto (~$1.20-2.16 USD/usuario/mes) pero real. No cambia la viabilidad del plan, solo corrige la proyección financiera.

---

## 1. CORRECCIONES A LAS US EXISTENTES ANTES DE SECUENCIAR

Revisé todas las US acumuladas (plan SDD original + análisis de brechas + adenda de validación + ciclo de vida) buscando huecos o duplicados. Encontré dos cosas que hay que resolver antes de ordenar:

**Duplicado — US-139 y US-155 son la misma US**
`US-139: Verificación de identidad para datos sensibles` (del análisis de brechas) y `US-155: Verificación de identidad para datos sensibles` (del documento de ciclo de vida) describen exactamente lo mismo. **Se consolidan en una sola: US-155 queda como la vigente** (tiene el flujo más específico de fecha de nacimiento + 3 intentos). US-139 se marca como superseded, no se implementa por separado.

**EP-10 necesita re-alcance, no eliminación**
`EP-10 — Plan semanal automático` (US-049 a US-052) se diseñó antes del modelo conversacional de la adenda de validación. Con el nuevo modelo (Koach negocia día a día, no entrega un plan fijo semanal), el alcance de EP-10 se reduce: ya no genera "el menú de la semana que debes seguir", sino un **resumen de macros de la semana + lista de compras proyectada** que sirve de referencia, no de mandato. Esto se especifica completo cuando se llegue a Fase 2 — aquí solo queda marcado para no perderlo de vista.

No se encontraron más huecos nuevos — el resto de US ya cubre lo necesario para lo que sigue.

---

## 2. PLAN SECUENCIAL — FASE 0 Y 1 (completamente especificado, listo para ejecutar)

Organizado en **hitos (M)**: cada uno agrupa US relacionadas y cierra con una prueba de uso concreta antes de pasar al siguiente. No es calendario — es orden de dependencia + puntos de verificación.

---

### M1 — Entorno de desarrollo
**US-000, US-001, US-002, US-003, US-004, US-005**
**≈ 12 horas**

Qué se construye: estructura del repo, entorno Python, esquema inicial de base de datos con RLS, FastAPI con health check, deploy a Railway, Sentry.

**✅ Prueba de uso:** `git clone` + seguir README levanta el proyecto de cero. `/health` responde 200 en producción por HTTPS.

---

### M2 — Capa de abstracción de IA
**US-006, US-007, US-008, US-009, US-010**
**≈ 14 horas** (↑ desde 12 — US-006 y US-009 ahora incluyen soporte de tool-use nativo, ver ADR-007 en el plan SDD)

Qué se construye: interfaces `LLMProvider` (con soporte de `tools`/`tool_calls`), proveedores Anthropic y Gemini, router con fallback (que respeta qué proveedores soportan tools), sistema de prompts versionados en YAML.

**✅ Prueba de uso:** llamar `AIRouter.complete()` manualmente con tier FAST y con tier SMART, confirmar respuesta de Gemini y Claude respectivamente. Apagar la API key de Anthropic a propósito y confirmar que el fallback a Gemini funciona sin que el sistema truene. Adicionalmente: llamar `AIRouter.complete()` con un `CompletionRequest` que incluya una tool de prueba y confirmar que Claude retorna `tool_calls` correctamente. Esta es la prueba más importante de toda la arquitectura — si esto funciona bien, la migración futura a IA local y el núcleo agéntico (M9 bis) están garantizados.

---

### M3 — Guardas de seguridad transversales
**US-134 (circuit breaker de costos), US-135 (defensa prompt injection), US-138 (rate limiting)**
**≈ 9 horas**

Por qué aquí y no después: estas guardas deben envolver **toda** llamada a IA desde el primer día, no agregarse al final cuando ya hay decenas de puntos de llamada sin protección.

**✅ Prueba de uso:** simular gasto que exceda el límite diario configurado y confirmar bloqueo automático. Mandar mensajes de prueba con intentos de "ignora tus instrucciones anteriores" y confirmar que el system prompt no se filtra en la respuesta. Mandar 15 mensajes en un minuto desde un mismo número de prueba y confirmar que el rate limit corta.

---

### M4 — Landing web
**US-011, US-012, US-013, US-014**
**≈ 8 horas** — puede hacerse en paralelo a M1-M3, no depende de ellas

**✅ Prueba de uso:** koach.mx accesible por HTTPS, el CTA abre WhatsApp con mensaje pre-llenado, el formulario de lead guarda registro real en Supabase.

---

### M5 — Canal de WhatsApp
**US-015, US-016, US-017, US-018, US-019**
**≈ 12 horas**

**✅ Prueba de uso:** con el número de prueba de Meta (no requiere verificación de negocio — la API funciona sin verificar, con tope de 250 conversaciones/día, suficiente para todo el MVP), mandar y recibir un mensaje real. Botones interactivos responden. Un template básico se envía correctamente.

---

### M6 — Estados de cuenta base
**US-153 (job de vencimiento de trial), US-154 (filtro de proactividad por estado)**
**≈ 4 horas**

Por qué aquí: todo lo que sigue (onboarding, mensajes proactivos) debe respetar el estado de la cuenta desde que existe el primer usuario de prueba, no parcharse después.

**✅ Prueba de uso:** crear usuario ficticio con `trial_ends_at` en el pasado, correr el job manualmente, confirmar que pasa a `inactive` y que el filtro de proactividad lo excluye correctamente.

---

### M7 — Onboarding conversacional
**US-020, US-021, US-022, US-023, US-024, US-025, US-155 (verificación identidad), US-156 (timeout abandono), US-158 (disclosure recurrente de IA)**
**≈ 22 horas**

**🎯 PRUEBA DE USO REAL #1 — la primera vez que el producto se siente vivo.**
Jaziel completa el onboarding completo desde su propio WhatsApp, de principio a fin, sin ayuda de nadie más: consentimiento LFPDPPP, mayoría de edad, 5 preguntas, PAR-Q, mensaje de bienvenida. Si esto se siente natural y rápido (~5 min), el hito está cumplido. Si se siente lento o confuso, es momento de ajustar antes de seguir — no después.

---

### M8 — Generación de planes base
**US-026, US-027, US-028, US-029, US-030**
**≈ 14 horas**

Nota: esto genera el **presupuesto de macros y el PDF de referencia inicial** — no el plan rígido semanal que el modelo conversacional reemplaza más adelante (ver sección 1). Sigue siendo necesario como base numérica.

**✅ Prueba de uso:** generar plan con datos ficticios y confirmar que el TDEE calculado coincide con el cálculo manual (test unitario). Confirmar que ningún alimento alérgeno declarado aparece en el plan generado por IA. Recibir el PDF por WhatsApp y que se vea profesional.

---

### M9 — Registro de actividad + protocolos de salud
**US-031 (alcance reducido, ver ADR-007), US-032, US-033, US-034, US-035, US-036, US-136 (detección TCA), US-137 (protocolo derivación)**
**≈ 23 horas** (↓ 1 hora — US-031 se redujo de clasificador principal a pre-filtro de comandos + screening de crisis)

Este es el hito más grande y el más delicado — junta el registro cotidiano con las dos detecciones más sensibles del producto. **Nota importante:** US-031 aquí ya NO es el router de intención hacia handlers — esa responsabilidad se mueve al loop agéntico de M9 bis. US-031 en este hito solo resuelve comandos exactos y hace el pre-screening barato de crisis antes de escalar a la verificación completa de US-032.

**🎯 PRUEBA DE USO REAL #2 — red-teaming deliberado (brecha 6.5 del análisis de brechas).**
Antes de seguir: registrar comidas reales propias durante varios días en lenguaje natural y confirmar que los cálculos son razonables. Después, diseñar 15-20 mensajes de prueba deliberadamente diseñados para disparar la detección de crisis y de TCA (frases límite, no reales) y confirmar que el protocolo correcto se activa cada vez — preferible sobre-detectar que fallar en silencio. Esta prueba debe hacerse **antes de invitar a cualquier persona externa**, sin excepción.

---

### M9 bis — Núcleo agéntico (ADR-007)
**US-159 (catálogo de herramientas), US-160 (bucle agéntico principal), US-161 (eval harness de tool-calling)**
**≈ 15 horas** (↑ desde 10 — agrega el mecanismo genérico "propone→confirma" y el eval harness)

Por qué aquí y no en M2: estas US envuelven funciones de dominio que todavía no existen hasta cerrar M9 (`registrar_comida`, `registrar_ejercicio`, `registrar_agua`, `registrar_peso` como funciones reales, no solo interfaces). Por qué antes de M10: el motor de proactividad de M10 ahora también pasa por este mismo loop (ver nota de M10 abajo) — tiene que existir primero.

Qué se construye: el catálogo formal de tools de Fase 1 (`registrar_comida`, `registrar_ejercicio`, `registrar_agua`, `registrar_peso`, `ajustar_horario_mensajes`, `activar_modo_silencio`, `derivar_a_profesional`, `marcar_crisis`, `confirmar_accion_pendiente`, `pedir_aclaracion`, más los placeholders de Fase 2 `actualizar_preferencia_alimentaria` y `buscar_contexto_historico`), el loop que orquesta (mensaje → Claude decide tools → se ejecutan → Claude redacta respuesta final), el mecanismo genérico de confirmación para tools de efecto grande, y el conjunto inicial de "conversaciones doradas" que valida en CI que el modelo elige bien las tools.

**🎯 PRUEBA DE USO REAL — el momento en que Koach se vuelve agente de verdad.**
Mandar un mensaje que mezcle dos intenciones en una sola frase (p. ej. "ya comí unos tacos y ya no me mandes mensajes en la tarde") y confirmar que ambas tools se invocan en el mismo turno y la respuesta final confirma las dos acciones. Probar también una tool `requiere_confirmacion` (p. ej. `ajustar_horario_mensajes` con un cambio grande) y confirmar que NO se aplica hasta que el usuario confirme explícitamente en el turno siguiente. Confirmar que una tool que falla a propósito (desconectar la DB momentáneamente) no rompe el turno — el usuario recibe una respuesta honesta, no un error crudo. Revisar `tool_calls_log` y confirmar que cada invocación quedó registrada con sus argumentos. Correr el eval harness (US-161) y confirmar que el set inicial de casos pasa.

---

### M10 — Motor de proactividad
**US-037, US-038 (ahora genera contenido vía el loop agéntico de M9 bis), US-039, US-040, US-041**
**≈ 16 horas** (↑ desde 14 — US-038 ya no dispara un template fijo, construye su propio request con tools y usa el mismo loop de M9 bis)

**✅ Prueba de uso:** configurar horarios de prueba cortos (cada 5-10 minutos en vez de horarios reales de todo el día) y confirmar que los mensajes llegan en la ventana correcta, respetando modo silencio y el filtro de estado de M6. Adicionalmente: confirmar que un check-in con alacena disponible sugiere algo coherente (usa `consultar_alacena`/`sugerir_comida`), y que apagar la API de Claude a propósito no deja al usuario sin mensaje — cae al template de respaldo (RF-7 de US-038).

---

### M11 — Rachas y resúmenes
**US-042, US-043, US-044**
**≈ 7 horas**

**✅ Prueba de uso:** simular una semana completa de registros (variando cumplimiento día a día) y confirmar que el cálculo de racha, reseteo y días de descanso funciona correctamente.

---

### M12 — Cumplimiento y panel antes de cobrar
**US-140 (exportación ARCO), US-141 (purga por retención), US-142 (panel admin), US-157 (activación manual de suscripción), US-144 (modo degradado)**
**≈ 18 horas**

**✅ Prueba de uso:** ejercer manualmente los tres comandos ARCO (`MIS DATOS`, `EXPORTAR MIS DATOS`, `BORRAR MIS DATOS`) con un usuario de prueba y confirmar que funcionan de principio a fin. Simular caída de la API de Claude (apagar la key) y confirmar que el sistema responde con mensaje amigable en vez de error crudo. Activar una suscripción de prueba desde el panel sin tocar Supabase directamente.

---

## 🎯 CIERRE DE FASE 0-1 — Prueba de uso real #3, la definitiva

Con M1 a M12 completos, el producto está listo para su primera prueba con personas reales fuera de Jaziel: 2-3 de los ya entrevistados que mostraron interés fuerte, usando Koach por WhatsApp durante varios días con supervisión cercana (revisar conversaciones diario los primeros días).

**Esto todavía no es "cobrar".** Es la validación de que el producto funciona de principio a fin antes de involucrar dinero — y coincide con el momento en que ya deberían estar resueltos el nutriólogo y las entrevistas restantes, según lo documentado en los pendientes.

---

## 3. RESUMEN DE HORAS — FASE 0-1 COMPLETA

| Hito | Horas |
|------|-------|
| M1 — Entorno de desarrollo | 12 |
| M2 — Capa de abstracción de IA | 14 |
| M3 — Guardas de seguridad | 9 |
| M4 — Landing web | 8 |
| M5 — Canal WhatsApp | 12 |
| M6 — Estados de cuenta base | 4 |
| M7 — Onboarding | 20 |
| M8 — Generación de planes | 14 |
| M9 — Registro + protocolos de salud | 23 |
| M9 bis — Núcleo agéntico (ADR-007) | 15 |
| M10 — Proactividad | 16 |
| M11 — Rachas | 7 |
| M12 — Cumplimiento y panel | 18 |
| **TOTAL** | **≈ 172 horas** |

**Nota honesta:** la versión original del plan estimaba ~110 horas para este mismo alcance (Fase 0 + Fase 1). Las primeras ~44 horas adicionales fueron el resultado de las revisiones de brechas, seguridad y ciclo de vida (circuit breaker, detección de TCA, ciclo de vida de cuentas, cumplimiento ARCO). Otras ~11 horas (M2 +2, M9 -1, M9 bis +10) fueron el costo inicial de rediseñar el núcleo del agente con tool-use nativo (ADR-007). Las ~7 horas más recientes (M9 bis +5, M10 +2) agregan el mecanismo genérico "propone→confirma", el eval harness de tool-calling (US-161), y que la proactividad misma pase por el loop agéntico en vez de templates fijos — no es que el plan se haya vuelto ineficiente, es que cada revisión encuentra algo que de verdad conviene resolver ahora y no después. Vale la inversión.

---

## 4. PANORAMA GENERAL — FASES SIGUIENTES (nivel de detalle menor)

Estas fases aún no tienen specs completas por US individual (solo se nombraron las épicas en el plan SDD original) — se detallan por completo cuando se llegue a ellas, siguiendo el mismo formato de este documento.

| Fase | Contenido | Horas estimadas |
|------|-----------|------------------|
| **Fase 2** — Nutrición completa | Alacena, modelo conversacional (US-145 a 148), EP-10 re-alcanzado, lista de compras, modo "Comí Fuera", audio, biblioteca de ejercicios, aprendizaje de patrones, registro por foto (EP-32) | ≈ 90-100 |
| **Fase 3** — App y Dashboard | Dashboard web, app móvil, reportes PDF, modo gym avanzado, notificaciones push | ≈ 80 |
| **Fase 4** — Chat nativo y monetización | Chat en app, pagos automatizados (Conekta real), CFDI, referidos, analytics | ≈ 80 |
| **Fase 5** — Perfiles y escala | Sistema de perfiles especializados, post-parto, adulto mayor, diabetes, migración a IA local | ≈ 90+ |

**Total aproximado del proyecto completo (Fase 0 a 5): ~490-500 horas.**

A tu ritmo de ~10 hrs/semana, eso son aproximadamente 48-50 semanas para el proyecto completo — pero **la Fase 0-1 (154 horas) es lo único que importa ahora mismo**, y con eso ya tienes un producto funcional de punta a punta que puedes probar con personas reales.

---

## 5. ORDEN RECOMENDADO SI EL TIEMPO ES IRREGULAR

Como no hay calendario fijo, esta es la guía de qué priorizar si solo tienes una sesión corta disponible:

- **Nunca saltar M3** (guardas de seguridad) por ahorrar tiempo — es la que más caro sale de omitir
- **M4 (landing) es la única que se puede posponer** sin afectar nada más — no depende de nada ni nada depende de ella
- **M9 es la más larga — dividirla en sub-sesiones está bien**, pero no empezar M9 bis sin haber cerrado la prueba de red-teaming de M9, ni empezar M10 sin haber cerrado la prueba del loop agéntico de M9 bis
- Si en algún punto el ritmo se detiene por semanas, lo único que hay que revisar al retomar es si `AI_STRATEGY` y las API keys siguen vigentes (M2) — todo lo demás es código estático que no se degrada con el tiempo

---

*Plan de Desarrollo Secuencial — Koach v1.2*
*Septiembre 2026*
