# KOACH — Ciclo de Vida del Usuario y Gestión de Cuentas
### Especificación de estados, activación de pagos y reglas operativas
> Complemento al Plan Maestro v6.0 y Plan SDD — Mayo 2026

---

## 1. DIAGRAMA DE ESTADOS

```
prospecto (no existe en DB)
    │ primer mensaje a WhatsApp
    ▼
  trial ─────────────────────────┐
    │ paga antes del día 7       │ día 7 sin pagar
    ▼                             ▼
  active                      inactive ◄──┐
    │ comando PAUSA               │       │
    ▼                             │       │ responde
  paused                          │       │ y quiere seguir
    │ reanuda / vence tiempo      │       │
    ▼                             │       │
  active ◄──────────────────────  │ ──────┘
    │ pide cancelar                │ 21 días sin responder
    ▼                              │ (desde active)
 cancelled ◄─────────────────────┘
    │ escribe de nuevo
    ▼
  trial (nueva prueba)
```

### Definición de cada estado

| Estado | Significado | Recibe proactividad |
|--------|-------------|---------------------|
| `trial` | Dentro de los 7 días de prueba | ✅ Sí, completa |
| `active` | Pagando, acceso completo | ✅ Sí, completa |
| `paused` | Pausó voluntariamente (comando PAUSA) | ❌ No, ninguna |
| `inactive` | Trial venció sin pago, o 21 días sin responder | ⚠️ Solo mensajes de reenganche |
| `cancelled` | Pidió explícitamente terminar | ❌ No, ninguna (salvo que regrese) |

**Distinción crítica:** `inactive` ≠ `cancelled`. `inactive` es "se apagó el acceso pero no dijo que ya no quiere" — sigue elegible a reenganche. `cancelled` es decisión explícita del usuario — no se le vuelve a contactar salvo que él escriba primero.

---

## 2. TRANSICIONES Y DISPARADORES

| De | A | Disparador | Automático o manual |
|----|---|------------|---------------------|
| — | `trial` | Primer mensaje de WhatsApp | Automático (US-020) |
| `trial` | `active` | Confirmación de pago recibida | **Manual en MVP** (revisar Conekta, actualizar Supabase) |
| `trial` | `inactive` | `trial_ends_at` vencido sin pago | **Automático desde el día 1** — job Celery diario |
| `active` | `paused` | Comando PAUSA | Automático |
| `paused` | `active` | Comando REANUDAR o vence duración elegida | Automático |
| `paused` | `cancelled` | 3 meses en pausa sin reanudar | Automático |
| `active` | `inactive` | 21 días sin interacción | Automático |
| `active` | `cancelled` | Usuario pide cancelar explícitamente | Automático tras confirmación |
| `inactive` | `active` o `trial` | Responde y quiere seguir (según si ya pagó antes) | Manual (mismo proceso que activación) |
| `cancelled` | `trial` | Escribe de nuevo | Automático — nueva prueba, re-evaluar estatus founder |
| `inactive` | *(purga)* | 60 días adicionales sin respuesta tras `inactive` | Marca `elegible_purga = true`, aplica política de retención (24 meses) |

---

## 3. ACTIVACIÓN DE PAGO — PROCESO PARA EL MVP (Meses 1-6)

**No se automatiza con webhooks de Conekta hasta EP-22 (Fase 4).** Antes de eso:

```
Día 6 de trial
    → Koach manda link de pago (Conekta Checkout hosteado, sin código)
    ↓
Usuario paga
    → Notificación llega al correo/dashboard de Conekta
    ↓
Jaziel entra a Supabase Table Editor
    → users.status = 'active'
    → users.plan_tier = 'coach' (o el que corresponda)
    → suscripciones.fecha_renovacion = hoy + 30 días
    ↓
El motor de proactividad ya revisa estos campos automáticamente
```

**Volumen manejable manualmente hasta:** ~30-40 usuarios/mes de conversiones. Migrar a EP-22 cuando esto tome más de 15-20 min diarios.

### Regla obligatoria desde el día 1 de código (no opcional)

El job de vencimiento de trial **sí debe ser automático desde el MVP**, aunque la activación sea manual:

```python
@celery.task
def check_trial_expirations():
    """Corre diario. Sin esto, usuarios sin pagar reciben servicio
    completo indefinidamente sin que nadie lo note."""
    vencidos = get_users(status="trial", trial_ends_at__lt=now())
    for user in vencidos:
        user.status = "inactive"
        send_template("trial_vencido", user)
```

### Regla para el motor de proactividad (agregar a spec de US-038)

```python
ESTADOS_CON_PROACTIVIDAD_COMPLETA = {"trial", "active"}
ESTADOS_CON_SOLO_REENGANCHE = {"inactive"}

def debe_recibir_mensaje(user, tipo_mensaje: str) -> bool:
    if user.status in ESTADOS_CON_PROACTIVIDAD_COMPLETA:
        return True
    if user.status in ESTADOS_CON_SOLO_REENGANCHE:
        return tipo_mensaje == "reenganche"
    return False  # paused, cancelled → nada
```

---

## 4. VERIFICACIÓN DE IDENTIDAD

### Antes de mostrar datos sensibles

```
Comando "MIS DATOS" o "BORRAR MIS DATOS"
    ↓
Koach: "Para tu seguridad, confírmame tu fecha de nacimiento"
    ↓
Coincide con perfiles.edad registrada → procede
No coincide (3 intentos) → "No pude verificar tu identidad.
                            Escríbenos a hola@koach.mx"
```

Aplica a: exportación de datos, eliminación de cuenta, cambio de número, consulta de historial completo. NO aplica a interacciones normales (registrar comida, ver plan del día) — sería fricción innecesaria.

### Onboarding abandonado a medias

```
conversacion_estado.flujo = 'onboarding' sin avanzar
    │ 48 horas sin respuesta
    ▼
Único mensaje de reactivación: "¿seguimos? aquí estoy cuando quieras"
    │ 7 días sin avanzar tras el mensaje
    ▼
conversacion_estado.estado = 'abandonado'
    (deja de insistir; el registro no se borra hasta política de retención)
```

---

## 5. MODELO DE DATOS — CAMPOS A AGREGAR

```sql
ALTER TABLE users ADD COLUMN elegible_purga BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN fecha_ultimo_cambio_estado TIMESTAMP;
ALTER TABLE users ADD COLUMN razon_estado_actual VARCHAR(100);

ALTER TABLE conversacion_estado ADD COLUMN estado VARCHAR(20) DEFAULT 'en_progreso';
-- valores: 'en_progreso', 'abandonado', 'completado'
```

---

## 6. NUEVAS USER STORIES

**US-153: Job de vencimiento automático de trial** (🔴 Crítica, 2 hrs)
Job Celery diario que mueve `trial` → `inactive` al vencer `trial_ends_at`.

**US-154: Filtro de estado en motor de proactividad** (🔴 Crítica, 2 hrs)
Implementar `debe_recibir_mensaje()` como guard obligatorio antes de cualquier envío proactivo.

**US-155: Verificación de identidad para datos sensibles** (🟠 Alta, 3 hrs)
Ya existía mencionada en el análisis de brechas (US-139) — esta la formaliza con el flujo exacto de fecha de nacimiento y 3 intentos.

**US-156: Timeout de onboarding abandonado** (🟠 Alta, 2 hrs)
Mensaje único a 48h, marca `abandonado` a 7 días.

**US-157: Panel manual de activación de suscripción** (🟠 Alta, 3 hrs)
Vista simple en el panel admin (EP-31/US-142) para cambiar `status` y `plan_tier` sin tocar Supabase directamente — reduce error humano en el proceso manual del punto 3.

---

*Ciclo de Vida del Usuario — Koach v1.0*
*Mayo 2026*
