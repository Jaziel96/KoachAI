# Plan — US-001: Webhook WhatsApp: recibir y verificar mensajes
## Generado por: Gemini | Fecha: 28 Mayo 2026

## 1. Entendimiento de la spec
Esta US establece el webhook para integrarse con la API de WhatsApp Cloud. Permite validar la conexión inicial con Meta mediante un reto (GET) y recibir mensajes de texto entrantes (POST). El sistema debe parsear el payload, extraer los datos clave, loggearlos y mandarlos a una función `handle_message` (vacía por ahora). Es crítico que el endpoint POST retorne HTTP 200 inmediatamente y no falle ante payloads no esperados.

## 2. Preguntas antes de planear
Sin preguntas — spec clara.

## 3. Archivos a CREAR
| Archivo | Responsabilidad |
|---------|----------------|
| `backend/app/api/endpoints/webhook.py` | Definir los endpoints GET y POST de `/webhook`. |
| `backend/app/schemas/whatsapp.py` | Modelos Pydantic (opcionales) o validación de diccionario para el payload de entrada. |
| `backend/app/services/whatsapp.py` | Definir la función vacía `handle_message(phone_number: str, message_text: str)`. |
| `backend/app/api/api.py` | (Recomendado) Router principal para agrupar endpoints e incluirlos limpiamente en `main.py`. |

## 4. Archivos a MODIFICAR
| Archivo | Qué cambia |
|---------|-----------|
| `backend/app/core/config.py` | Agregar la variable obligatoria `whatsapp_verify_token: str`. |
| `backend/.env.example` | Añadir `WHATSAPP_VERIFY_TOKEN=tu_token_aqui`. |
| `backend/app/main.py` | Incluir el router del webhook para que los endpoints estén expuestos. |

## 5. Esquema de DB (si aplica)
No aplica.

## 6. Dependencias nuevas (si aplica)
No hay dependencias nuevas necesarias (FastAPI y Pydantic son suficientes).

## 7. Orden de implementación
1. Modificar `config.py` y `.env.example` para incorporar `WHATSAPP_VERIFY_TOKEN` asegurando que levante error si falta.
2. Crear `backend/app/services/whatsapp.py` con la función base `handle_message`.
3. Crear `backend/app/api/endpoints/webhook.py` y escribir la lógica del GET (verificación) y POST (recepción y parseo).
4. Usar `BackgroundTasks` de FastAPI en el POST si es necesario para asegurar que la respuesta 200 se envíe antes de hacer procesos pesados en futuras US (buena práctica desde ahora).
5. Conectar el nuevo endpoint en `main.py`.

## 8. Riesgos identificados
| Riesgo | Probabilidad | Mitigación |
|--------|-------------|-----------|
| Timeout de Meta (retardo > 1s) | Baja en MVP, Alta a futuro | Usar `BackgroundTasks` para el procesamiento del mensaje y retornar 200 de inmediato. |
| Caída por payload inesperado | Media | Envolver el parseo del payload en `try...except`, loggear el error y siempre retornar HTTP 200. |
| Falta del token de verificación | Baja | Pydantic fallará en el arranque de la app, lo cual cumple CE-01 (falla en inicio, no en runtime). |

## 9. Impacto en US existentes
Impacto nulo, únicamente se añade sobre la base creada en US-000.

## ✅ Plan listo para implementación
