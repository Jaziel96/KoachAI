# Instrucciones para Claude Code — Proyecto Koach

## Contexto

Koach es un agente de salud proactivo por WhatsApp para mexicanos, especializado en
orientación alimentaria (NOM-043-SSA2-2012) y acompañamiento de hábitos — **no es un
servicio médico ni de nutrición clínica**. Lee `docs/plan-desarrollo-sdd.md` (arquitectura
y User Stories completas) y `docs/plan-desarrollo-secuencial.md` (orden de ejecución por
hitos M1-M12, con horas y pruebas de uso) antes de implementar cualquier cosa.

Documentos de referencia en `docs/`:
- `plan-desarrollo-sdd.md` — arquitectura técnica, ADRs, estructura del proyecto, User Stories detalladas (US-000 en adelante)
- `plan-desarrollo-secuencial.md` — el orden real de ejecución (hitos M1-M12), con horas estimadas y una prueba de uso concreta al cierre de cada hito. **Sigue este orden**, no actives épicas fuera de secuencia.
- `analisis-brechas.md` — especifica EP-31 (US-134 a US-144): circuit breaker de costos, prompt injection, detección de TCA, protocolo de derivación, rate limiting, panel admin, ARCO, retención de datos
- `ciclo-vida-usuario.md` — especifica US-153 a US-157: estados de cuenta, activación de pago, verificación de identidad
- `adenda-legal-pendientes.md` — marco NOM-043 y lenguaje obligatorio del producto

## Reglas técnicas NO NEGOCIABLES

1. **NUNCA importar SDKs de IA directamente en lógica de negocio.**
   Todo acceso a IA pasa por `app/ai/` (ver ADR-002 y ADR-007 en `docs/plan-desarrollo-sdd.md`).

2. **NUNCA hardcodear prompts en código Python.**
   Los prompts van en `app/ai/prompts/` como YAML (ADR-003).

3. **NUNCA guardar secretos en código.**
   Usar `app/core/config.py` con Pydantic Settings.

4. **SIEMPRE type hints.** El proyecto usa mypy en strict mode.

5. **SIEMPRE RLS en tablas nuevas de Supabase** (ADR-006).

6. **Mensajes al usuario en español mexicano**, código en inglés.

7. **Koach es agéntico, no un router de clasificación (ADR-007).** El flujo de un mensaje
   entrante NO es "clasificar intención → llamar handler fijo". Es: pre-filtro barato de
   comandos exactos + screening de crisis (US-031, alcance reducido) → si no aplica, el
   mensaje entra al bucle agéntico (US-160), donde Claude recibe el catálogo de
   herramientas (US-159) y decide cuáles invocar. No reintroduzcas un clasificador de
   intención como router principal — ya se decidió explícitamente en contra de eso.

8. **Ninguna tool sensible (`registrar_peso`, `derivar_a_profesional`, `marcar_crisis`)
   confía ciegamente en lo que decide el modelo.** Cada una valida sus propios límites en
   código determinista (ver ADR-007, principio de defense-in-depth). Los límites de
   seguridad viven en las funciones, nunca solo en el prompt.

9. **La detección de crisis (US-032) y de trastornos alimentarios (US-136) tienen
   prioridad absoluta e independiente del loop agéntico.** Nunca se tratan como "una tool
   más" entre otras — corren como guard previo, y si detectan señal, el turno normal ni
   se ejecuta.

10. **Toda invocación de herramienta se audita** en `tool_calls_log` / `historial_conversacion`
    (nombre, argumentos, resultado, éxito/error) — es un requisito de seguridad, no opcional.

11. **Límites de seguridad conservadores de contenido** (definidos en `docs/analisis-brechas.md`
    y `docs/adenda-legal-pendientes.md`): déficit calórico máximo 20%, mínimo 1400 kcal
    mujeres / 1700 hombres, pérdida semanal máxima 0.75% del peso corporal. Nunca generar
    contenido que sugiera valores fuera de estos rangos.

12. **Lenguaje del producto:** nunca usar "plan nutricional", "dieta" (como prescripción),
    "tratamiento", "diagnóstico", "nutriólogo virtual". Usar "orientación alimentaria",
    "guía de alimentación", "acompañamiento", "coach de hábitos saludables".

## Antes de implementar cualquier User Story

1. Lee la spec completa en `docs/plan-desarrollo-sdd.md` (o en `docs/analisis-brechas.md` /
   `docs/ciclo-vida-usuario.md` si la US pertenece a EP-31 o al ciclo de vida)
2. Verifica en `docs/plan-desarrollo-secuencial.md` en qué hito (M1-M12) cae, y confirma que
   los hitos previos ya están cerrados (no saltar de orden — hay dependencias reales)
3. Verifica dependencias con otras US listadas en la spec
4. Propón un plan de implementación antes de escribir código, y espera aprobación

## Comandos frecuentes

- Tests: `pytest -v`
- Lint: `ruff check . && mypy app`
- Migración: `alembic revision --autogenerate -m "descripcion"`
- Dev server: `uvicorn app.main:app --reload`

## Definition of Done (resumen — ver sección 8 de `docs/plan-desarrollo-sdd.md`)

- [ ] Todos los criterios de aceptación de la US se cumplen
- [ ] Tests unitarios pasan con la cobertura mínima de la capa (`domain/` 90%, `services/` 70%, `adapters/` 50%, `api/` 60%)
- [ ] `ruff check` y `mypy` sin errores
- [ ] Migración de DB aplicada y reversible (si aplica)
- [ ] Probado manualmente según la "✅ Prueba de uso" del hito correspondiente en `docs/plan-desarrollo-secuencial.md`
