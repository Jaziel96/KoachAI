# US-001 — Webhook WhatsApp: recibir y verificar mensajes

## Contexto
Toda la comunicación de Koach llega a través de un webhook que
Meta (WhatsApp Cloud API) llama cada vez que un usuario envía un
mensaje. Sin este endpoint funcionando correctamente, ninguna otra
US puede probarse en condiciones reales. Es la tubería base del sistema.

## Descripción
Como sistema Koach, necesito recibir y verificar los mensajes
entrantes de WhatsApp, para poder procesarlos en las siguientes US.

## Requisitos funcionales
- RF-01: Endpoint GET /webhook que responda el challenge de
  verificación de Meta (parámetros: hub.mode, hub.verify_token,
  hub.challenge)
- RF-02: Endpoint POST /webhook que reciba mensajes entrantes
  y retorne HTTP 200 inmediatamente
- RF-03: Extraer del payload: número de teléfono del remitente,
  tipo de mensaje y texto del mensaje
- RF-04: Loggear cada mensaje recibido con timestamp, número
  y contenido
- RF-05: Estructura preparada para pasar el mensaje a un handler
  (la lógica del handler va en US-002, aquí solo la firma)

## Requisitos no funcionales
- RNF-01: Responder HTTP 200 a Meta en menos de 1 segundo
  (si tarda más, Meta reintenta y genera duplicados)
- RNF-02: Si el payload es inválido o inesperado, loggear
  el error y retornar 200 de todas formas (Meta requiere 200
  siempre, los errores se manejan internamente)
- RNF-03: El verify_token debe venir de variable de entorno,
  nunca hardcodeado

## Flujo principal — Verificación (GET)
1. Meta llama GET /webhook con hub.mode="subscribe",
   hub.verify_token y hub.challenge
2. Sistema verifica que hub.verify_token coincide con
   la variable de entorno WHATSAPP_VERIFY_TOKEN
3. Si coincide: retorna hub.challenge como texto plano (HTTP 200)
4. Si no coincide: retorna HTTP 403

## Flujo principal — Mensaje entrante (POST)
1. Meta llama POST /webhook con payload JSON
2. Sistema retorna HTTP 200 inmediatamente
3. Sistema extrae: phone_number, message_type, message_text
4. Sistema loggea el mensaje recibido
5. Sistema llama a handle_message(phone_number, message_text)
   (función vacía por ahora, se implementa en US-002)

## Flujos alternativos
- FA-01 — Payload no es de tipo "text": loggear tipo recibido
  y retornar 200 sin procesar (voice, image, etc. se manejan
  en US futuras)
- FA-02 — Payload malformado o sin la estructura esperada:
  loggear warning con el payload raw y retornar 200

## Casos de error
- CE-01: WHATSAPP_VERIFY_TOKEN no definido en .env →
  levantar error al iniciar la app, no en runtime
- CE-02: Meta no recibe 200 → reintento automático de Meta,
  el log debe permitir identificar duplicados por message_id

## Criterios de aceptación
- [ ] CA-01: GET /webhook con token correcto retorna el challenge
- [ ] CA-02: GET /webhook con token incorrecto retorna 403
- [ ] CA-03: POST /webhook retorna 200 en menos de 1 segundo
- [ ] CA-04: Los datos del mensaje aparecen en el log
- [ ] CA-05: Payload malformado no rompe el servidor
- [ ] CA-06: WHATSAPP_VERIFY_TOKEN viene de variable de entorno
- [ ] CA-07: La función handle_message existe aunque esté vacía

## Decisiones técnicas previas
- Framework: FastAPI (ya configurado en US-000)
- Para probar localmente sin aprobación de Meta:
  usar curl o Postman para simular los llamados
- El payload de Meta tiene esta estructura:
  ```json
  {
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "521234567890",
            "type": "text",
            "text": {"body": "Hola"},
            "id": "wamid.xxx"
          }]
        }
      }]
    }]
  }
  ```

## Fuera de scope
- Enviar respuestas de vuelta al usuario → US-002
- Lógica de onboarding o conversación → US-002
- Autenticación de usuarios → US-002
- Manejo de mensajes de voz, imagen u otros tipos → US futuras

## Referencias
- Docs WhatsApp Cloud API webhooks:
  https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks
- Plan de ejecución: Semana 1, días 3-5
- US relacionadas: US-002 (depende de esta)
