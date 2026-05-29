# Plan — US-002: Detección de usuario y onboarding conversacional
## Generado por: Gemini | Fecha: 29 Mayo 2026

## 1. Entendimiento de la spec
Esta US construye el núcleo conversacional inicial. El sistema ahora debe poder identificar el número de teléfono del usuario consultando a la base de datos (Supabase). Si es nuevo, inicia un flujo estructurado de recopilación de datos (onboarding) mediante una máquina de estados de 7 pasos. Es fundamental el manejo del consentimiento por motivos de la LFPDPPP, y que toda respuesta enviada por Koach esté centralizada en un diccionario de mensajes en español (`es_mx.py`). Además, se introduce la capacidad de envío de mensajes hacia la API de WhatsApp.

## 2. Preguntas antes de planear
Sin preguntas — spec clara. Asumiremos que el cliente de Supabase oficial (`supabase-py`) se usará para gestionar las tablas.

## 3. Archivos a CREAR
| Archivo | Responsabilidad |
|---------|----------------|
| `backend/scripts/init_db_us002.sql` | Almacenar las sentencias DDL (CREATE TABLE) indicadas en la spec para la DB. |
| `backend/app/db/supabase.py` | Configurar e instanciar el cliente oficial de Supabase. |
| `backend/app/messages/es_mx.py` | Diccionario centralizado con todos los mensajes que el bot envía al usuario (bienvenida, preguntas, errores, etc). |
| `backend/app/services/whatsapp_sender.py` | Servicio encargado de enviar mensajes (POST) a la Graph API de Meta usando `httpx`. |
| `backend/app/services/onboarding.py` | Contener la lógica de negocio, la validación y el avance de los 7 pasos del onboarding. |

## 4. Archivos a MODIFICAR
| Archivo | Qué cambia |
|---------|-----------|
| `backend/app/core/config.py` | Añadir `whatsapp_phone_number_id` obligatorio. |
| `backend/.env.example` | Agregar `WHATSAPP_PHONE_NUMBER_ID=123456789...`. |
| `backend/requirements.txt` | Añadir `httpx` para peticiones HTTP asíncronas de salida. |
| `backend/app/services/whatsapp.py` | Implementar `handle_message` para consultar Supabase, enrutar hacia el onboarding o saludar si ya existe. |

## 5. Esquema de DB (si aplica)
Se ejecutarán en la consola SQL de Supabase:
```sql
CREATE TABLE usuarios ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), phone_number TEXT UNIQUE NOT NULL, nombre TEXT NOT NULL, created_at TIMESTAMPTZ DEFAULT NOW() );
CREATE TABLE perfiles ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE, edad INTEGER NOT NULL, peso_kg DECIMAL(5,2) NOT NULL, talla_cm INTEGER NOT NULL, genero TEXT NOT NULL, meta TEXT NOT NULL, alergias TEXT DEFAULT 'ninguna', created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW() );
CREATE TABLE consentimientos ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE, acepto BOOLEAN NOT NULL, fecha TIMESTAMPTZ DEFAULT NOW(), version_aviso TEXT DEFAULT '1.0' );
CREATE TABLE onboarding_estado ( id UUID PRIMARY KEY DEFAULT gen_random_uuid(), phone_number TEXT UNIQUE NOT NULL, paso_actual INTEGER DEFAULT 0, datos_parciales JSONB DEFAULT '{}', intentos_paso INTEGER DEFAULT 0, created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW() );
```

## 6. Dependencias nuevas (si aplica)
- Se requiere agregar `httpx` al `requirements.txt` para enviar las solicitudes asíncronas a WhatsApp Graph API sin bloquear el event loop.

## 7. Orden de implementación
1. Actualizar `config.py`, `.env.example` y añadir `httpx` en `requirements.txt`.
2. Crear archivo SQL para las tablas y aplicarlo en la base de datos real.
3. Configurar conexión en `backend/app/db/supabase.py`.
4. Escribir los textos en `backend/app/messages/es_mx.py`.
5. Crear `backend/app/services/whatsapp_sender.py` con el método para enviar texto.
6. Programar la máquina de estados y las validaciones en `backend/app/services/onboarding.py`.
7. Interconectar todo en `handle_message` dentro de `backend/app/services/whatsapp.py`.
8. Escribir tests unitarios probando flujos de onboarding simulando la base de datos.

## 8. Riesgos identificados
| Riesgo | Probabilidad | Mitigación |
|--------|-------------|-----------|
| Fallos en el parseo de datos (ej. "peso 70" o "1.70m") | Alta | Usar validaciones flexibles (regex) en el onboarding. Si no se puede extraer un número claro, pedir al usuario que reintente en un formato simple antes de guardar basura. |
| Bloqueo del servidor enviando msjs | Media | Usar cliente asíncrono (`httpx.AsyncClient`) dentro del context de FastAPI/BackgroundTasks. |
| Falla al conectar con DB Supabase | Baja | Atrapar excepciones de DB en `handle_message` y responder el string genérico de "problema técnico" (CE-01). |

## 9. Impacto en US existentes
- Actualiza `whatsapp.py` que fue el punto final (stub) de la US-001, sin romper el endpoint HTTP que ya funciona bien (gracias a `BackgroundTasks`).

## ✅ Plan listo para implementación
