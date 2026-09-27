# KOACH — Análisis de Brechas
### Auditoría de seguridad, legal y operativa antes de desarrollar
> Documento crítico — v1.1, Septiembre 2026

---

## RESUMEN EJECUTIVO

Revisión completa del plan buscando lo que falta. **34 brechas** clasificadas por severidad.

| Severidad | Cantidad | Significado |
|-----------|----------|-------------|
| 🔴 Crítica | 7 | Puede detener el proyecto o generar responsabilidad legal seria |
| 🟠 Alta | 11 | Debe resolverse antes de tener usuarios de pago |
| 🟡 Media | 10 | Debe resolverse en los primeros 6 meses |
| 🟢 Baja | 6 | Mejoras deseables |

**La brecha más grave es legal, no técnica.** Ver sección 1.1.

---

# PARTE 1 — BRECHAS LEGALES

## 🔴 1.1 CRÍTICA — Ejercicio profesional de la nutrición

Koach calcula déficits calóricos y genera guías de alimentación para bajar de peso — cerca de "nutrición clínica"/"tratamiento de obesidad", que en México requiere cédula profesional (Ley General de Salud, NOM-008-SSA3-2017).

**Resuelto formalmente** vía NOM-043-SSA2-2012 — ver `koach-adenda-legal-pendientes.md`: Koach se posiciona como ORIENTACIÓN ALIMENTARIA Y ACOMPAÑAMIENTO DE HÁBITOS (personal capacitado ejecuta materiales validados por personal calificado/nutriólogo con cédula).

**Cambios obligatorios de lenguaje:**

| ❌ Nunca usar | ✅ Usar en su lugar |
|--------------|---------------------|
| "Plan nutricional" | "Guía de alimentación" / "Orientación alimentaria" |
| "Dieta" (prescriptiva) | "Estilo de alimentación" / "Hábitos" |
| "Tratamiento" | "Acompañamiento" |
| "Prescribimos" | "Sugerimos" / "Orientamos" |
| "Diagnóstico" | (nunca) |
| "Nutriólogo virtual" | "Coach de hábitos saludables" |
| "Bajarás X kilos" | "Te acompañamos hacia tu meta" |

**Validación profesional — requisito antes de cobrar:** contratar nutriólogo con cédula (Opción A, $3,000-8,000 MXN una vez + $1,000-2,000/mes), migrar después al modelo de Asesor/Nutriólogo Fundador con comisión por referido inverso.

**Protocolo de derivación obligatoria** ante: IMC>35, IMC<18.5, condición médica declarada, embarazo/lactancia, señales de TCA, menores de 18, mayores de 70, medicamentos que afecten metabolismo, solicitud de dietas muy restrictivas.

**Límites de seguridad conservadores:** déficit máx. 20% (no 25%), mínimo 1400 kcal mujeres / 1700 hombres, pérdida semanal máx. 0.75% del peso corporal.

## 🔴 1.2 CRÍTICA — Términos y Condiciones incompletos

Cláusulas obligatorias: naturaleza del servicio (orientación alimentaria, NO médico), limitación de responsabilidad, disclaimer de IA, ausencia de garantía de resultados, obligaciones del usuario, suspensión/terminación, suscripciones y renovación automática (requisitos PROFECO), jurisdicción (Colima), propiedad intelectual, modificaciones con 15 días de aviso.

## 🟠 1.3 ALTA — Transferencia internacional de datos

Datos de salud procesados en Anthropic/Google/OpenAI/Supabase (EE.UU.). Requiere cláusula explícita en el aviso de privacidad, revisión de políticas de retención de cada proveedor, evaluar Zero Data Retention, y minimizar qué se envía a la IA (nunca nombre completo/teléfono/email).

## 🟠 1.4 ALTA — Registro sanitario / COFEPRIS

Probablemente NO requerido (software de orientación, no dispositivo médico) mientras nunca se diagnostique, recomienden medicamentos, o se publicite como tratamiento médico. Requiere consulta con abogado especialista ($3,000-5,000 MXN).

## 🟡 1.5 MEDIA — Publicidad y marketing

Prohibido: "Baja 10 kilos en un mes", "Cura la diabetes", "Reemplaza a tu nutriólogo". Permitido con disclaimer de resultados individuales.

## 🟡 1.6 MEDIA — Contrato entre cofundadores

Aportaciones, división de responsabilidades, reparto de utilidades, propiedad de código/marca, salida, decisiones, vesting.

---

# PARTE 2 — BRECHAS DE SEGURIDAD

## 🔴 2.1 CRÍTICA — Control de costos de IA (circuit breaker) → US-134

```python
class CostGuard:
    LIMITE_DIARIO_USD = 15.0
    LIMITE_MENSUAL_USD = 300.0
    LIMITE_POR_USUARIO_DIARIO_USD = 0.50

    async def check_before_call(self, user_id: UUID, estimated_cost: float) -> None:
        gasto_hoy = await self.get_gasto_diario()
        if gasto_hoy + estimated_cost > self.LIMITE_DIARIO_USD:
            await self.alert_admin("Límite diario de IA alcanzado")
            raise CostLimitExceededError()
        gasto_usuario = await self.get_gasto_usuario_hoy(user_id)
        if gasto_usuario > self.LIMITE_POR_USUARIO_DIARIO_USD:
            raise UserQuotaExceededError()
```

**Nota v1.1 (ADR-007):** debe envolver también el bucle agéntico (US-160) — cada iteración de tool-calling cuenta contra el límite por usuario.

## 🔴 2.2 CRÍTICA — Prompt injection → US-135

Defensa en 4 capas: separación estructural (nunca concatenar input al system prompt), detección de patrones sospechosos, validación de salida, aislamiento de contexto entre usuarios.

**Nota v1.1 (ADR-007):** con tool-use nativo la superficie de ataque crece (un injection podría intentar disparar una tool sensible). Por eso las tools sensibles validan en código determinista y toda tool call queda en `tool_calls_log`.

## 🔴 2.3 CRÍTICA — Suplantación de identidad por WhatsApp → US-139 (consolidada en US-155)

SIM swap, número reasignado, celular prestado. Solución: verificación por fecha de nacimiento, re-verificación tras 60+ días de inactividad, nunca datos sensibles en mensajes proactivos.

## 🟠 2.4 ALTA — Autenticación de la app (Fase 3)

JWT, vinculación WhatsApp↔app por código de 6 dígitos, recuperación de cuenta, 2FA opcional.

## 🟠 2.5 ALTA — Panel de administración → US-142

2FA obligatorio, log inmutable de accesos, mínimo privilegio (Maira solo métricas agregadas).

## 🟠 2.6 ALTA — Validación de archivos subidos → US-143

MIME real, 5MB máx, strip de EXIF (GPS en fotos de progreso), nunca renderizar como HTML, URLs firmadas de expiración corta.

## 🟠 2.7 ALTA — Abuso del número de WhatsApp → US-138

Rate limiting (10/min, 60/hora, 200/día), número de respaldo, monitoreo de quality rating en Meta.

## 🟡 2.8 MEDIA — Política de retención de datos → US-141

Perfil activo: mientras la cuenta esté activa. Registros: 24 meses. Conversación: 12 meses. Facturación: 5 años. Cuenta cancelada: purga a 30 días.

## 🟡 2.9 MEDIA — Backups y recuperación

Prueba de restauración trimestral, segundo proveedor, RTO 4h, RPO 24h.

## 🟡 2.10 MEDIA — Escaneo de dependencias

Dependabot, pip-audit, npm audit, pin de versiones.

## 🟡 2.11 MEDIA — Rotación de secretos

Procedimiento de 6 pasos cada 90 días.

## 🟢 2.12 BAJA — Pentesting

Antes de 100 usuarios, $15,000-30,000 MXN, mes 9-12.

---

# PARTE 3 — BRECHAS DE PRODUCTO

## 🟠 3.1 ALTA — Recuperación de cuenta

Pérdida de teléfono, cambio de número, desinstalación. Falta flujo vinculado a email.

## 🟠 3.2 ALTA — Detección de trastornos alimentarios → US-136

Señales: peso reportado con frecuencia excesiva, <1000 kcal por 3+ días, menciones de purgar/compensar, IMC<18.5 con meta de bajar más. Protocolo: dejar de dar info calórica → mensaje empático → recursos (Línea de la Vida: 800 911 2000) → sugerir profesional → marcar para revisión manual.

## 🟡 3.3 MEDIA — Zonas horarias en viaje

Comando "estoy viajando a [lugar]".

## 🟡 3.4 MEDIA — Exportación de datos ARCO → US-140

`EXPORTAR MIS DATOS` → ZIP con link de 48h.

## 🟡 3.5 MEDIA — Comportamiento offline y errores → US-144

Mensajes amigables si IA/WhatsApp/DB caen, nunca error crudo.

## 🟢 3.6 BAJA — Accesibilidad

Mensajes legibles sin depender de emojis/formato visual.

---

# PARTE 4 — BRECHAS OPERATIVAS

## 🟠 4.1 ALTA — Jaziel no disponible

Runbook ejecutable por Maira, contacto de emergencia técnica, mensaje automático a usuarios si hay caída prolongada.

## 🟠 4.2 ALTA — Soporte al usuario

Comando `SOPORTE`, SLA 24h hábiles.

## 🟡 4.3 MEDIA — Monitoreo de negocio

Alertas: conversión cae >20%, churn semanal >10%, sin usuarios nuevos en 3 días, costo IA sube >50%/semana.

## 🟡 4.4 MEDIA — Proceso de rollback

Rollback en Railway documentado, migraciones siempre reversibles, feature flags.

---

# PARTE 5 — BRECHAS DE NEGOCIO

## 🟡 5.1 MEDIA — Unit economics por usuario

Margen < 60% es señal de alerta. Ver `koach-analisis-costos-actualizado.md` para cifras reales corregidas.

## 🟡 5.2 MEDIA — Protocolo si un usuario reporta daño

Documentar → no admitir responsabilidad sin asesoría legal → contactar con empatía → preservar logs → abogado → evaluar seguro ($5,000-15,000 MXN/año, mes 6).

## 🟢 5.3 BAJA — Monitoreo de competencia

Revisión mensual de Fitia, Zapia, Google Health.

---

# PARTE 6 — BRECHAS DE LA REVISIÓN PROFESIONAL FINAL

| # | Brecha | Severidad | Cuándo se atiende | ¿Bloquea código? |
|---|--------|-----------|---------------------|-------------------|
| 6.1 | Políticas de uso de IA de los proveedores para salud/bienestar | 🔴 | Antes de código de producción | ✅ Resuelta (Parte 7) |
| 6.2 | Riesgo de calendario de verificación de negocio en Meta | 🟠 | Semana 1, en paralelo | No — resuelto mejor de lo esperado (Parte 7) |
| 6.3 | Fraude de pago y contracargos | 🟠 | Antes de cobrar (semana 5) | No |
| 6.4 | Riesgo cambiario USD/MXN | 🟡 | Mes 3 | No |
| 6.5 | QA conversacional y red-teaming | 🔴 | Antes del primer beta — integrado en M9 | Gate de calidad interno |
| 6.6 | Moderación de contenido / abuso hacia Koach | 🟠 | Semana 3, con el system prompt | No |
| 6.7 | Rollback de prompts | 🟡 | Semana 2-3, con Git/CI | No |
| 6.8 | Post-mortems de incidentes | 🟡 | Mes 2+ | No |

---

# PARTE 7 — RESOLUCIÓN DE POLÍTICAS DE IA Y META

## 7.1 Políticas de IA — RESUELTO

**Anthropic:** excluye explícitamente "wellness advice (sleep, stress, nutrition, exercise)" de su categoría de Alto Riesgo — Salud. Prohíbe facilitar autolesión/TCA/crítica de imagen corporal (valida US-136). Exige disclosure de IA al inicio de cada sesión → **US-158**.

**OpenAI (Whisper):** riesgo bajo, solo transcripción.
**Google (Gemini, tier FAST):** riesgo bajo.

## 7.2 Meta — mejor de lo esperado

Cloud API funciona sin verificación de negocio completa (tope 250 conversaciones/24h) — suficiente para MVP y beta.

## 7.3 Resolución sobre "acciones controversiales" en crisis

Se decidió NO tomar acciones autónomas más agresivas (911 automático, notificar contacto de emergencia sin consentimiento, risk scoring, contención prolongada) — mantiene el diseño original de US-032 (detectar → derivar → nunca actuar solo). Cualquiera de esas acciones activaría la categoría de Alto Riesgo de Anthropic y añade riesgo legal sin respaldo profesional.

## 7.4 US-158: Disclosure recurrente de IA

Informar al usuario al inicio de cada sesión de conversación (no solo onboarding) que habla con IA. Se integra a la lógica de "nueva sesión" (ver M7 del plan secuencial).

---

# PLAN DE ACCIÓN PRIORIZADO

**Antes de escribir código (semana 1-2):** consulta legal, redefinir lenguaje, contactar nutriólogo, redactar T&C, definir retención de datos.

**Antes del primer beta (semana 3-4):** CostGuard, defensas prompt injection, detección TCA, límites conservadores, protocolo de derivación, rate limiting.

**Antes de cobrar (semana 5-6):** validación de nutriólogo firmada, T&C publicados, aviso de privacidad con transferencia internacional, ARCO funcional, runbook básico, contrato entre cofundadores.

**Primeros 3 meses:** panel admin, prueba de restauración, alertas de negocio, Dependabot, rotación de secretos.

**Meses 4-12:** nutriólogo como asesor formal, seguro de responsabilidad civil, pentesting, registro de marca IMPI.

---

# NUEVAS USER STORIES — EP-31 (Seguridad y Cumplimiento)

US-134 Circuit breaker de costos de IA (🔴, 3h) · US-135 Defensas prompt injection (🔴, 4h) · US-136 Detección de TCA (🔴, 4h) · US-137 Protocolo de derivación (🔴, 3h) · US-138 Rate limiting (🟠, 2h) · US-139 Verificación de identidad (🟠, 3h — *superseded por US-155*) · US-140 Exportación ARCO (🟠, 3h) · US-141 Retención/purga (🟡, 3h) · US-142 Panel admin (🟠, 6h) · US-143 Validación de archivos/EXIF (🟠, 2h) · US-144 Modo degradado (🟡, 3h).

**Total: ~36 horas.**

---

# CONCLUSIÓN

**No escribir código de producción hasta resolver la brecha 1.1** — ya resuelta documentalmente vía NOM-043 (`koach-adenda-legal-pendientes.md`), pendiente la consulta legal (P-03) y la contratación del nutriólogo (P-01). Todo lo demás (circuit breaker, prompt injection, TCA, ciclo de vida, ARCO) sí se resuelve con código y ya está especificado en las US de este documento y en `koach-plan-desarrollo-sdd.md`.

---

*Koach — Análisis de Brechas v1.1 (integra Parte 6, Parte 7, y notas de ADR-007)*
*Septiembre 2026*
