# KOACH — Índice Maestro de Documentos
### Guía de navegación del proyecto
> Última actualización: Septiembre 2026 — agrega el rediseño agéntico (ADR-007) y sus refinamientos (confirmación genérica, proactividad vía el loop, eval harness) al plan SDD y al plan secuencial. También registra que TODOS los documentos de este índice ya están concentrados en el repositorio real, en `docs/` (ver tabla abajo).
> Úsese como punto de entrada — lee esto primero antes que cualquier otro documento

---

## 🎯 CÓMO USAR ESTE ÍNDICE

Este proyecto tiene varios documentos generados en distintos momentos de la planeación. Algunos se quedaron parcialmente obsoletos por decisiones posteriores. Este índice te dice:

1. Qué contiene cada documento
2. Cuál es la fuente de verdad vigente para cada tema
3. Qué está resuelto y qué sigue pendiente
4. Por dónde retomar según en qué momento estés
5. Dónde vive cada documento en el repositorio real (`docs/`)

---

## 📚 LOS DOCUMENTOS

| # | Documento (claude.ai) | Ruta en el repo (`docs/`) | Qué contiene | Vigencia |
|---|-----------|---------------------------|--------------|----------|
| 1 | `koach-plan-maestro-v6.md` | `plan-maestro.md` | Producto, arquitectura, negocio, marketing — documento base completo, incluye el esquema de base de datos completo (sección 14) | ⚠️ Parcialmente superado (ver correcciones abajo) — trae su propia nota de vigencia al inicio del archivo en el repo |
| 2 | `koach-analisis-competencia.md` | `analisis-competencia.md` | Investigación de Fitia, Zapia, Smart Fit Coach, Google Health y otros | ✅ Vigente — solo contexto de negocio, no técnico |
| 3 | `koach-analisis-brechas.md` | `analisis-brechas.md` | Auditoría de seguridad, legal y operativa — 34 brechas + Parte 6 (revisión final) + Parte 7 (resolución de políticas de IA y Meta) | ✅ Vigente — Parte 7 es lo más reciente sobre políticas de proveedores de IA |
| 4 | `koach-adenda-legal-pendientes.md` | `adenda-legal-pendientes.md` | Marco legal NOM-043, rol del nutriólogo, registro de pendientes | ✅ **Fuente de verdad legal actual** |
| 5 | `koach-plan-ejecucion-3meses.md` | `plan-ejecucion-3meses.md` | Plan semana a semana, setup técnico, primeros 3 meses | ⚠️ Presupuesto, numeración de US y estructura de carpetas desactualizados — trae su propia nota de vigencia al inicio del archivo en el repo |
| 6 | `koach-plan-desarrollo-sdd.md` | `plan-desarrollo-sdd.md` | Arquitectura técnica, épicas, 47+ User Stories detalladas | ✅ Vigente — v1.2. v1.1 agregó ADR-007, extendió US-006/US-009, redujo alcance de US-031, agregó US-159/US-160. v1.2 agrega el patrón "propone→confirma" genérico, extiende US-038 (proactividad vía el loop agéntico) y agrega US-161 (eval harness de tool-calling). Pendiente agregar EP-31 y EP-32 formalmente (ver abajo) |
| 7 | `koach-adenda-validacion-modelo-conversacional.md` | `adenda-validacion-modelo-conversacional.md` | Hallazgos de entrevistas + rediseño del modelo de sugerencia de comidas + diseño de registro por foto | ✅ Vigente |
| 8 | `koach-ciclo-vida-usuario.md` | `ciclo-vida-usuario.md` | Estados de cuenta, activación de pago, verificación de identidad | ✅ Vigente |
| 9 | `koach-plan-desarrollo-secuencial.md` | `plan-desarrollo-secuencial.md` | Orden de ejecución por hitos (M1-M12, incluyendo M9 bis), horas, pruebas de uso en cada punto | ✅ Vigente — v1.2, total ahora ≈172 hrs Fase 0-1 |

**Nota sobre costos:** no existe un documento separado "de costos actualizados" — las correcciones de costo real de WhatsApp Cloud API y comparativa de proveedores de IA viven dentro de `analisis-brechas.md` y de la nota de vigencia al inicio de `plan-maestro.md`. (Una versión anterior de este índice mencionaba un documento `koach-analisis-costos-actualizado.md` que nunca llegó a crearse como archivo independiente — se corrige aquí para evitar confusión.)

**Regla general de jerarquía:** cuando dos documentos se contradicen, gana el más reciente. Orden cronológico: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9. `CLAUDE.md` en la raíz del repo apunta a cada uno de estos archivos con las mismas reglas de vigencia.

---

## 🔄 CORRECCIONES VIGENTES (lo que cambió después de escrito el documento original)

### Sobre el Plan Maestro v6.0 (doc 1)

| Tema en el doc original | Estado actual | Dónde está la corrección |
|--------------------------|----------------|---------------------------|
| Plan nutricional como "plan fijo semanal" | ❌ Reemplazado por modelo conversacional de negociación diaria | Doc 7, Parte 2 |
| Precio objetivo $299 MXN plan Coach | ⚠️ En duda — 3 entrevistas sugieren disposición real ~$137 MXN | Doc 7, Parte 1.2 — pendiente confirmar con 12 entrevistas más |
| "Nutriólogo consultor" como mejora en mes 6 | 🔴 Ahora es **requisito antes de cobrar**, no opcional | Doc 4, sección 1.1 |
| Lenguaje "plan nutricional", "dieta", "prescribimos" | ❌ Debe evitarse por riesgo de ejercicio profesional no autorizado | Doc 4, sección 1.6 |
| Registro por foto listado sin detalle técnico | ✅ Diseño completo con pipeline de 4 pasos | Doc 7, Parte 3 |
| Sin circuit breaker de costos de IA | 🔴 Brecha crítica identificada, ahora es US-134 | Doc 3, sección 2.1 |
| Sin defensa de prompt injection | 🔴 Brecha crítica identificada, ahora es US-135 | Doc 3, sección 2.2 |
| Sin detección de trastornos alimentarios | 🔴 Brecha crítica identificada, ahora es US-136 | Doc 3, sección 3.2 |
| Costo de WhatsApp Cloud API asumido en $0 | ⚠️ Corregido — ~$1.20-2.16 USD/usuario/mes real | Doc 3, sección de costos |

### Sobre el Plan de Ejecución 3 Meses (doc 5)

| Tema en el doc original | Estado actual |
|--------------------------|----------------|
| Presupuesto inicial ~$850-2,950 MXN | ⚠️ Ajustar: con validación de nutriólogo + legal, inversión real ronda $12,000-17,000 MXN distribuidos (ver doc 4, Parte 2) |
| No contemplaba semana de validación previa | 🔴 Las entrevistas (doc 7) deben completarse ANTES de escribir código de producción |
| Cronograma no incluye tiempo para brechas de seguridad (EP-31) | Agregar ~36 hrs / 1 semana extra al cronograma técnico |
| Numeración de US-001 a US-008 y estructura de carpetas | ❌ Reemplazadas por la numeración real de `plan-desarrollo-sdd.md` y la arquitectura hexagonal (ADR-001) |

### Sobre el Plan SDD (doc 6)

**Cambio arquitectónico ya integrado (v1.1, septiembre 2026):** Koach pasa de un diseño "clasificar-y-rutear" (un clasificador de intención decide la categoría del mensaje y el backend rutea a un handler fijo) a una **arquitectura agéntica con tool-use nativo de Anthropic** (ADR-007). Claude recibe el mensaje, el contexto y un catálogo de herramientas (`tools`), y decide él mismo cuáles invocar — incluyendo varias en un mismo turno. Esto ya está reflejado en:
- ADR-007 (nueva sección en Parte I)
- US-006 y US-009 extendidas para soportar `tools`/`tool_calls`
- US-031 con alcance reducido (ya no es el router principal, solo pre-filtro de comandos exactos + pre-screening de crisis)
- US-159 (catálogo de herramientas) y US-160 (bucle agéntico principal) — nuevas, en EP-06 bis
- Reflejado también en doc 9 como el nuevo hito M9 bis

**Nuevo (septiembre 2026): ADR-008 — Dashboard también en web.** Para maximizar cobertura
de mercado, el dashboard (Fase 3) se construye como rutas autenticadas dentro del mismo
proyecto Next.js del sitio de marketing (`koach.mx`), no solo dentro de la app nativa —
cualquiera puede usarlo desde el navegador sin instalar nada. La app móvil (React Native +
Expo) sigue construyéndose como canal adicional, no como prerrequisito. Ver ADR-008 completo
en doc 6, y el hito de Fase 3 actualizado en doc 9.

**Pendiente de agregar formalmente al documento** (mencionado en otros docs pero no integrado a la numeración de épicas):

- **EP-31 — Seguridad y Cumplimiento** (US-134 a US-144, ~36 hrs) — detallado en doc 3, sección final
- **EP-32 — Registro por Foto** (US-149 a US-152) — detallado en doc 7, Parte 4
- **Ampliación a EP-09** con US-145 a US-148 (modelo conversacional de gustos) — detallado en doc 7, Parte 4

---

## 🚦 ESTADO GENERAL DEL PROYECTO

### ✅ Resuelto y con decisión tomada
- Nombre: Koach
- Stack técnico completo (FastAPI, Supabase, multi-IA con abstracción para migrar a local)
- Arquitectura de capa de IA agnóstica de proveedor
- Estructura legal: Persona Física (Maira) → SAS futuro
- Marco normativo identificado: NOM-043-SSA2-2012 habilita el modelo
- Modelo conversacional de comida (negociación, no prescripción)
- Metodología SDD con specs y User Stories detalladas
- Todos los documentos de planeación concentrados en el repositorio real (`docs/`), referenciados desde `CLAUDE.md`

### 🔴 Pendiente crítico — bloquea avanzar a código de producción
- [ ] **Completar 12 entrevistas de validación restantes** (van 3/15) — doc 7, Parte 1
- [ ] Contactar y contratar nutriólogo con cédula (Nivel 1 mínimo) — doc 4, Parte 3
- [ ] Consulta legal de confirmación (1-2 hrs) — doc 4, Parte 2
- [ ] Confirmar o descartar precio $149-299 con muestra diversa de entrevistas

### 🟠 Pendiente alto — antes de cobrar el primer peso
- [ ] Redacción final de T&C con cláusulas específicas (doc 3, sección 1.2)
- [ ] Aviso de privacidad con transferencia internacional de datos (doc 3, sección 1.3)
- [ ] Contrato entre cofundadores (doc 3, sección 1.6)
- [ ] Implementar US-134 a US-137 (circuit breaker, prompt injection, TCA, derivación)

### 🟡 Pendiente medio — primeros meses de operación
- Ver tablas de pendientes completas en doc 3 (Parte 5) y doc 4 (Parte 2)

---

## 🗺️ RUTA DE LECTURA SEGÚN TU MOMENTO

**"Quiero recordar la visión general del producto"**
→ Doc 1 (Plan Maestro), secciones 1-4 — pero lee las correcciones arriba primero

**"Voy a hacer las siguientes entrevistas de validación"**
→ Doc 7, Parte 1 (hallazgos hasta ahora) + guion original en el historial de chat

**"Voy a hablar con el nutriólogo"**
→ Doc 4, Parte 3 completa (documento de alcance, qué firma, cómo abordarlo)

**"Voy a empezar a escribir código"**
→ Doc 6 (Plan SDD) para arquitectura y US + Doc 7 Parte 2-3 para el modelo conversacional actualizado + recuerda agregar EP-31 y EP-32 antes de considerar el plan completo

**"Necesito revisar qué falta legalmente"**
→ Doc 3 (Análisis de Brechas) completo + Doc 4 (marco NOM-043 resuelto)

**"Quiero recordar contra quién compito"**
→ Doc 2 (Análisis de Competencia) completo, sigue vigente

**"Voy a platicar con Maira del plan operativo"**
→ Doc 5 (Plan de Ejecución 3 Meses), con las correcciones de presupuesto arriba

---

## 📌 LAS 3 DECISIONES MÁS IMPORTANTES PENDIENTES

Si solo tuvieras que resolver tres cosas antes de seguir avanzando, son estas:

**1. ¿El precio real es $149 o más bajo?**
Las 3 entrevistas apuntan a ~$137 MXN de disposición real. Esto afecta el modelo de negocio completo (break-even, proyecciones). Se resuelve con las siguientes entrevistas, priorizando gente fuera del círculo cercano.

**2. ¿Quién es el nutriólogo y qué validará?**
Sin esto, no puedes cobrar sin riesgo legal real. Es la brecha que más bloquea el avance. Doc 4 ya trae todo listo para abordarlo — falta ejecutar la conversación.

**3. ¿El modelo conversacional (doc 7) reemplaza o convive con el plan semanal fijo (doc 1)?**
Técnicamente ya se decidió que lo reemplaza, y ya se reflejó consistentemente en el plan SDD (EP-09 ampliada, US-145 a US-148). Falta que se refleje también en todo el material de marketing cuando se retome ese trabajo.

---

*Índice Maestro Koach v1.3*
*Generado para organizar el proyecto en claude.ai y mantenerlo espejado 1:1 con el repositorio real*
