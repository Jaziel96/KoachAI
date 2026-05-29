# US-003 — Generación del plan inicial con Claude API

## Contexto
Al completar el onboarding, el usuario espera recibir su plan
personalizado. Esta US convierte los datos capturados en US-002
en un plan real de alimentación y ejercicio generado por Claude API.
Es el primer momento de valor tangible para el usuario — cuando
Koach deja de ser un formulario y se convierte en un coach real.

## Descripción
Como usuario que completó el onboarding, quiero recibir un plan
personalizado de alimentación y ejercicio por WhatsApp, para
saber exactamente qué comer y hacer desde el día 1.

## Requisitos funcionales
- RF-01: Al completar el onboarding, disparar automáticamente
  la generación del plan (reemplaza el logger.info de US-002)
- RF-02: Recuperar el perfil completo del usuario desde Supabase
  (tabla `perfiles` + `usuarios`)
- RF-03: Calcular el TDEE del usuario usando la fórmula
  Mifflin-St Jeor antes de llamar a Claude
- RF-04: Construir un prompt estructurado con los datos del
  usuario y enviarlo a Claude API
- RF-05: Claude genera el plan con esta estructura exacta:
  - Resumen del perfil (datos calculados: TMB, TDEE, meta calórica)
  - Plan de alimentación del día 1 (desayuno, comida, cena, snacks)
  - Plan de ejercicio semanal (3-4 días, tipo según meta)
  - 3 consejos personalizados según las alergias/condiciones
- RF-06: Guardar el plan generado en tabla `planes` en Supabase
- RF-07: Enviar el plan al usuario por WhatsApp en mensajes
  separados (máximo 1,500 caracteres por mensaje)
- RF-08: Registrar en logs el tiempo de generación del plan

## Requisitos no funcionales
- RNF-01: La generación del plan no debe bloquear el webhook —
  ejecutarse como BackgroundTask
- RNF-02: Tiempo máximo de generación: 30 segundos
- RNF-03: Si Claude API falla, reintentar 1 vez antes de
  enviar mensaje de error al usuario
- RNF-04: El prompt a Claude debe estar en un archivo separado
  `app/prompts/plan_inicial.py`, no hardcodeado en el servicio
- RNF-05: El modelo a usar es claude-sonnet-4-20250514

## Fórmula Mifflin-St Jeor
```
Hombre: TMB = (10 × peso_kg) + (6.25 × talla_cm) - (5 × edad) + 5
Mujer:  TMB = (10 × peso_kg) + (6.25 × talla_cm) - (5 × edad) - 161
Otro:   Promedio de ambas fórmulas

Factor de actividad (MVP — todos sedentarios por default):
TDEE = TMB × 1.2

Meta calórica:
- Bajar de peso:   TDEE - 300 kcal
- Ganar músculo:   TDEE + 250 kcal
- Comer mejor:     TDEE (mantenimiento)
- Más energía:     TDEE (mantenimiento)
```

## Flujo principal
1. US-002 llama a `generar_plan_inicial(phone_number)` al
   completar el onboarding
2. Sistema recupera perfil del usuario desde Supabase
3. Sistema calcula TMB, TDEE y meta calórica
4. Sistema construye el prompt con los datos calculados
5. Sistema llama a Claude API (claude-sonnet-4-20250514)
6. Claude responde con el plan estructurado
7. Sistema guarda el plan en tabla `planes`
8. Sistema divide el plan en mensajes de ≤1,500 chars
9. Sistema envía cada mensaje por WhatsApp con pausa de 1s
   entre mensajes para no saturar la API
10. Sistema loggea tiempo total de generación

## Flujos alternativos
- FA-01 — Claude API falla en primer intento: esperar 2s
  y reintentar una vez más
- FA-02 — Claude API falla en reintento: enviar mensaje
  al usuario explicando el problema y que se generará
  su plan en los próximos minutos. Loggear error crítico.
- FA-03 — Plan generado supera 4,000 caracteres: dividir
  en múltiples mensajes automáticamente

## Casos de error
- CE-01: Perfil no encontrado en DB → log error, no enviar
  mensaje (no debería ocurrir si US-002 funcionó bien)
- CE-02: Timeout de Claude API (>30s) → tratar como FA-01
- CE-03: Error al guardar plan en Supabase → loggear pero
  continuar y enviar el plan al usuario de todas formas

## Criterios de aceptación
- [ ] CA-01: Al completar onboarding, el usuario recibe
  su plan en WhatsApp sin acción adicional
- [ ] CA-02: El plan incluye TMB, TDEE y meta calórica correctos
- [ ] CA-03: El plan incluye alimentación del día 1 con
  desayuno, comida, cena y snacks
- [ ] CA-04: El plan incluye rutina de ejercicio semanal
- [ ] CA-05: Las alergias del usuario se respetan en el plan
- [ ] CA-06: El plan queda guardado en tabla `planes`
- [ ] CA-07: Si Claude falla, el usuario recibe mensaje
  de error amable (no silencio)
- [ ] CA-08: Cada mensaje WhatsApp tiene ≤1,500 caracteres
- [ ] CA-09: El prompt está en `app/prompts/plan_inicial.py`
- [ ] CA-10: El tiempo de generación queda en los logs

## Esquema de DB requerido

```sql
CREATE TABLE planes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    contenido TEXT NOT NULL,
    tmb DECIMAL(7,2),
    tdee DECIMAL(7,2),
    meta_calorica DECIMAL(7,2),
    generado_en DECIMAL(5,2),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Decisiones técnicas previas
- Usar `anthropic` SDK (ya en requirements.txt)
- El cliente de Anthropic también debe envolverse en
  `asyncio.to_thread` igual que Supabase (patrón establecido
  en US-002)
- Los mensajes de espera mientras se genera el plan van
  en `es_mx.py` (patrón establecido)
- Agregar a `es_mx.py`:
  - GENERANDO_PLAN: "⏳ ¡Perfecto! Estoy analizando tu perfil
    y generando tu plan personalizado. Esto toma unos segundos..."
  - ERROR_GENERANDO_PLAN: "Tuve un problema generando tu plan.
    No te preocupes, lo intentaré de nuevo en unos minutos 🔄"

## Fuera de scope
- Actualización del plan después del día 1 → US futura
- Plan en formato PDF → US-008
- Ajuste del plan según progreso → US futura
- Factor de actividad personalizado → US futura
  (todos los usuarios arrancan como sedentarios)

## Referencias
- Plan maestro: Módulo de Planes y Nutrición
- US relacionadas: US-002 (la dispara), US-008 (PDF del plan)
- Docs Anthropic SDK: https://docs.anthropic.com/en/api/messages
