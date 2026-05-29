# US-002 — Detección de usuario y onboarding conversacional

---
## Estado: ✅ COMPLETADA
**Fecha de implementación:** 29 Mayo 2026
**Commit:** 3831005 (feat(US-002): implement user detection and conversational onboarding)
**Archivos principales:** `backend/app/services/onboarding.py`, `backend/app/messages/es_mx.py`, `backend/app/services/whatsapp_sender.py`
**Notas finales:** Se validó que el uso de `asyncio.to_thread` es la práctica oficial y recomendada para encapsular llamadas síncronas de `supabase-py` v2 en un contexto asíncrono, garantizando el rendimiento de la aplicación.
---

## Contexto
Cuando llega un mensaje al webhook (US-001), el sistema necesita
saber quién está escribiendo y qué hacer con ese mensaje. Si el
número no existe en la base de datos, se inicia el onboarding —
un flujo conversacional de 7 preguntas que captura los datos
necesarios para generar el plan personalizado del usuario.
Este es el primer punto donde Koach realmente "habla" con alguien.

## Descripción
Como nuevo usuario de Koach, quiero que el sistema me reconozca
automáticamente como usuario nuevo, me explique qué es Koach,
me pida mi consentimiento y me haga preguntas simples una por una,
para poder recibir mi plan personalizado desde el primer día.

## Requisitos funcionales
- RF-01: Implementar handle_message (stub de US-001) que detecte
  si el número existe en la tabla `usuarios`
- RF-02: Si el número no existe, iniciar flujo de onboarding
- RF-03: Enviar mensaje de bienvenida y solicitar consentimiento
  LFPDPPP antes de cualquier pregunta de datos personales
- RF-04: Si el usuario rechaza el consentimiento, responder con
  mensaje de cierre y no guardar ningún dato
- RF-05: Si acepta, hacer 7 preguntas en orden, una por una:
  1. ¿Cuál es tu nombre?
  2. ¿Cuántos años tienes?
  3. ¿Cuánto pesas actualmente? (kg)
  4. ¿Cuánto mides? (cm)
  5. ¿Cuál es tu género? (hombre / mujer / prefiero no decir)
  6. ¿Cuál es tu meta principal? (bajar de peso / ganar músculo /
     comer mejor / más energía)
  7. ¿Tienes alguna alergia o condición alimentaria que deba
     conocer? (o escribe "ninguna")
- RF-06: Persistir el estado del onboarding entre mensajes en
  la tabla `onboarding_estado` con paso_actual y datos_parciales
- RF-07: Validar cada respuesta antes de avanzar al siguiente paso
- RF-08: Al completar las 7 preguntas, crear registros en
  `usuarios` y `perfiles`, registrar consentimiento en
  `consentimientos`, y enviar mensaje de confirmación
- RF-09: Enviar mensajes de vuelta al usuario vía WhatsApp
  Cloud API (primera vez que el sistema responde de verdad)

## Requisitos no funcionales
- RNF-01: El estado del onboarding persiste si el usuario
  abandona — al volver, Koach retoma desde la última pregunta
- RNF-02: Mensajes claros, en español mexicano, tono amigable
  y conversacional — no robótico
- RNF-03: Todas las respuestas de Koach al usuario viven en
  `app/messages/es_mx.py`, nunca hardcodeadas en el handler
- RNF-04: El envío de mensajes debe pasar por un servicio
  centralizado `whatsapp_service.send_message()`

## Flujo principal
1. Llega mensaje POST al webhook → handle_message se ejecuta
2. Sistema busca phone_number en tabla `usuarios`
3. No existe → verificar si hay onboarding en curso en
   `onboarding_estado`
4. No hay onboarding → enviar bienvenida + solicitar consentimiento
5. Usuario responde "sí" / "acepto" / "si" → guardar consentimiento,
   iniciar preguntas desde paso 1
6. Sistema hace pregunta 1, guarda estado paso_actual=1
7. Usuario responde → validar → guardar en datos_parciales →
   avanzar a pregunta 2
8. Repetir hasta completar las 7 preguntas
9. Crear `usuarios`, `perfiles`, `consentimientos`
10. Enviar mensaje: "¡Listo [nombre]! Estoy generando tu plan..."
11. Disparar señal para US-003 (por ahora solo log)

## Flujos alternativos
- FA-01 — Usuario rechaza consentimiento: enviar mensaje de
  cierre con link al aviso de privacidad. No guardar nada.
  No bloquear el número (puede volver a intentarlo)
- FA-02 — Usuario abandona a mitad: al volver, Koach saluda
  por nombre (si ya lo capturó) y retoma desde donde dejó
- FA-03 — Usuario ya existe en `usuarios`: no iniciar
  onboarding, pasar a handler de conversación (US-004,
  por ahora solo responder "¡Hola de nuevo [nombre]!")
- FA-04 — Respuesta inválida en una pregunta: Koach repite
  la pregunta con ejemplo del formato esperado.
  Máximo 3 intentos antes de sugerir escribir "reiniciar"

## Casos de error
- CE-01: Error de conexión a Supabase → log del error,
  responder al usuario "Tuve un problema técnico, intenta
  en unos minutos"
- CE-02: Edad menor de 13 años → mensaje amable de exclusión,
  no guardar datos
- CE-03: Peso fuera de rango (< 20kg o > 400kg) → pedir
  confirmación antes de guardar
- CE-04: WHATSAPP_TOKEN no válido al enviar → log crítico,
  no romper el servidor

## Criterios de aceptación
- [ ] CA-01: Número nuevo recibe mensaje de bienvenida y
  solicitud de consentimiento
- [ ] CA-02: Rechazo de consentimiento → ningún dato guardado
  en DB, mensaje de cierre enviado
- [ ] CA-03: Aceptación → pregunta 1 enviada, estado guardado
  en onboarding_estado
- [ ] CA-04: Respuesta inválida → mensaje de ayuda, misma
  pregunta repetida, sin avanzar de paso
- [ ] CA-05: Al completar las 7 preguntas → registros creados
  en usuarios, perfiles y consentimientos
- [ ] CA-06: Usuario que abandona retoma desde donde dejó
- [ ] CA-07: Menor de 13 años no puede completar el onboarding
- [ ] CA-08: Usuario existente recibe "¡Hola de nuevo [nombre]!"
- [ ] CA-09: Todos los mensajes al usuario vienen de es_mx.py
- [ ] CA-10: El envío se hace via whatsapp_service.send_message()

## Esquema de DB requerido

```sql
-- Tabla principal de usuarios
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Perfil de salud del usuario
CREATE TABLE perfiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    edad INTEGER NOT NULL,
    peso_kg DECIMAL(5,2) NOT NULL,
    talla_cm INTEGER NOT NULL,
    genero TEXT NOT NULL,
    meta TEXT NOT NULL,
    alergias TEXT DEFAULT 'ninguna',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Registro de consentimientos LFPDPPP
CREATE TABLE consentimientos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    acepto BOOLEAN NOT NULL,
    fecha TIMESTAMPTZ DEFAULT NOW(),
    version_aviso TEXT DEFAULT '1.0'
);

-- Estado del onboarding en curso
CREATE TABLE onboarding_estado (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number TEXT UNIQUE NOT NULL,
    paso_actual INTEGER DEFAULT 0,
    datos_parciales JSONB DEFAULT '{}',
    intentos_paso INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Decisiones técnicas previas
- El envío de mensajes requiere WHATSAPP_TOKEN (token de página
  de Meta) y WHATSAPP_PHONE_NUMBER_ID — agregar a config.py
- Para enviar mensajes usar la API de WhatsApp Cloud:
  POST https://graph.facebook.com/v18.0/{phone_number_id}/messages
- Los mensajes al usuario son texto simple por ahora
  (no botones ni listas — eso es US futura)
- El handler de conversación para usuarios existentes (US-004)
  queda como stub: solo responde "¡Hola de nuevo [nombre]!"

## Fuera de scope
- Generación del plan nutricional → US-003
- Flujo de conversación diaria → US-004
- Mensajes con botones o listas interactivas → US futura
- Notificaciones proactivas → US-005
- Manejo de mensajes de voz o imagen → US futura

## Referencias
- Plan maestro: Módulo 9 — Onboarding Progresivo
- US relacionadas: US-001 (depende de), US-003 (la dispara)
- Docs WhatsApp Send Messages:
  https://developers.facebook.com/docs/whatsapp/cloud-api/messages
