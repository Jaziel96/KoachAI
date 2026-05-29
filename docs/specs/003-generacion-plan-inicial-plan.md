# Plan — US-003: Generación del plan inicial con Claude API
## Generado por: Gemini | Fecha: 29 Mayo 2026

## 1. Entendimiento de la spec
Esta historia de usuario representa el "momento mágico" (Aha moment) de la aplicación. Convierte los datos estáticos del usuario recolectados en el onboarding en un plan nutricional y de entrenamiento usando IA (Claude). La lógica requiere orquestar cálculos matemáticos de salud (Mifflin-St Jeor), una llamada API externa con Claude usando un prompt estructurado, guardar el resultado en base de datos, fraccionar la respuesta en chunks más pequeños (<1500 caracteres) y enviarlos secuencialmente. 

Por diseño del proyecto, las peticiones a la API oficial síncrona de Anthropic deben envolverse con `asyncio.to_thread` para no bloquear el servicio asíncrono de FastAPI.

## 2. Preguntas antes de planear
Sin preguntas — spec clara y el precedente técnico del SDK síncrono se resolvió en la US-002.

## 3. Archivos a CREAR
| Archivo | Responsabilidad |
|---------|----------------|
| `backend/scripts/init_db_us003.sql` | Instrucciones DDL para crear la tabla `planes`. |
| `backend/app/prompts/plan_inicial.py` | Definición de la constante string con el prompt y la estructura que Claude debe seguir. |
| `backend/app/services/claude.py` | Servicio que interactúa con la API de Anthropic, encapsulado en un wrapper asíncrono y manejando el reintento. |
| `backend/app/services/plan.py` | Orquestador: calcula TMB/TDEE, solicita la respuesta a Claude, la guarda en Supabase, la divide y la envía por WhatsApp. |

## 4. Archivos a MODIFICAR
| Archivo | Qué cambia |
|---------|-----------|
| `backend/app/messages/es_mx.py` | Agregar las constantes `GENERANDO_PLAN` y `ERROR_GENERANDO_PLAN`. |
| `backend/app/services/onboarding.py` | Modificar la función `_complete_onboarding` para que envíe el mensaje de espera y llame a `generar_plan_inicial()`. |

## 5. Esquema de DB (si aplica)
Se creará la siguiente tabla en Supabase:
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

## 6. Dependencias nuevas (si aplica)
No aplica. `anthropic` SDK ya está preconfigurado en los requerimientos del proyecto.

## 7. Orden de implementación
1. Escribir y ejecutar `init_db_us003.sql`.
2. Actualizar `es_mx.py` agregando los textos indicados.
3. Crear `app/prompts/plan_inicial.py` asegurando que instruya claramente al modelo sobre las alergias y metas.
4. Crear `app/services/claude.py`. Inicializar el cliente `Anthropic()` y crear un método `generate_plan` que ejecute el reintento usando `try...except`, enviando el proceso al ThreadPool con `asyncio.to_thread`.
5. Desarrollar `app/services/plan.py` implementando:
   - Fórmulas de TMB (diferenciado por género) y TDEE (factor 1.2 sedentario constante).
   - Ajuste de meta calórica (bajar de peso -300, ganar músculo +250).
   - Función helper `_chunk_message()` que parta textos largos en bloques ≤ 1,500 caracteres, preferiblemente buscando dobles saltos de línea `\n\n` hacia atrás para no cortar frases a la mitad.
   - Orquestador final.
6. Enganchar la llamada de este orquestador al final del `_complete_onboarding` en `onboarding.py`.

## 8. Riesgos identificados
| Riesgo | Probabilidad | Mitigación |
|--------|-------------|-----------|
| Bloqueo del Event Loop por Claude | Alta | Usar estrictamente `asyncio.to_thread` para las llamadas al SDK de Anthropic como se hizo con `supabase-py`. |
| Fallo en red/API de Meta por mensajes largos | Media | Desarrollar un "chunker" inteligente que garantice un máximo duro de 1,500 caracteres y colocar un `asyncio.sleep(1)` entre envíos de un mismo plan. |
| Caída del servicio Claude | Baja | Reintentar la llamada API tras 2 segundos. Si el fallo persiste, notificar activamente al usuario en lugar de dejarlo esperando. |

## 9. Impacto en US existentes
- **US-001**: Ninguno. El request de Meta sigue cerrándose en <1s porque `BackgroundTasks` encapsula el proceso completo.
- **US-002**: Se elimina un mensaje quemado en `onboarding.py` y se enlaza este flujo final.

## ✅ Plan listo para implementación
