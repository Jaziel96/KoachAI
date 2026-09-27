> ## ⚠️ NOTA DE VIGENCIA (leer antes que el resto del documento)
>
> Este documento es el plan de ejecución original semana a semana (mayo 2026), escrito
> **antes** de la arquitectura real del proyecto. Se incluye en el repo por completitud
> histórica y de contexto de negocio — **no es una guía técnica vigente para Claude Code.**
> Concretamente:
>
> - La numeración de User Stories (US-001 a US-008 aquí) **no corresponde** a la
>   numeración real y definitiva en `docs/plan-desarrollo-sdd.md` — no uses estos números.
> - La estructura de carpetas del backend (`app/routes/`, `app/services/`, `app/models/`)
>   fue reemplazada por la arquitectura hexagonal (domain/ports/adapters/services/api) —
>   ver ADR-001 en `docs/plan-desarrollo-sdd.md`.
> - El router "clasificar y rutear" implícito en varias tareas aquí fue reemplazado por la
>   arquitectura agéntica (ADR-007) — ver `docs/plan-desarrollo-sdd.md`.
> - El orden real de ejecución vigente es el de `docs/plan-desarrollo-secuencial.md`
>   (hitos M1-M12), no el calendario semana a semana de este documento.
> - Las cifras de inversión y presupuesto están desactualizadas — ver corrección de
>   costos reales de WhatsApp Cloud API y validación de nutriólogo en
>   `docs/analisis-brechas.md` y `docs/adenda-legal-pendientes.md`.
> - El pricing de $99-149 MXN mencionado aquí para los primeros usuarios está en duda —
>   ver `docs/adenda-validacion-modelo-conversacional.md`, Parte 1.
>
> **Lo que sigue siendo útil de este documento:** el contexto operativo/de negocio para
> Jaziel y Maira (setup de cuentas, redes, dominios, checklist de negocio), y como
> referencia histórica de cómo se pensó originalmente el arranque del proyecto.

---

# KOACH — Plan de Ejecución Detallado
## Primeros 3 meses desde cero
> Desde configuración de laptop personal hasta 30+ usuarios pagando
> Adaptado a: 10 hrs/semana + 1 semana de vacaciones intensiva

---

## 🎯 RESUMEN DEL PLAN

| Fase | Semanas | Tiempo | Objetivo |
|------|---------|--------|----------|
| **Setup y validación** | 1-3 | 30 hrs (10/sem) | Configuración + página web + validación |
| **Vacaciones intensivas** | 4 | 40 hrs | MVP funcional end-to-end |
| **Iteración y escalamiento** | 5-12 | 80 hrs (10/sem) | 30+ usuarios pagando |

**Cuándo tomar las vacaciones:** Semana 4, ya que tendrás configuración lista y específicas listas para implementar.

---

# 📅 SEMANA 1 — Configuración total del entorno

## 🎯 Objetivo de la semana
Tener tu laptop personal configurada para desarrollar Koach con SDD. Empezar branding y comprar dominios.

---

## DÍA 1 — LUNES (1 hora)

### Tarea 1.1 — Instalar herramientas básicas en laptop personal (30 min)

Asumiendo que ya tienes VS Code instalado. Instalar lo que falta:

**Paso 1: Instalar Git**
- Windows: descargar de git-scm.com → instalar con opciones por default
- Mac: ya viene preinstalado (verificar con `git --version` en terminal)
- Verificar instalación abriendo terminal: `git --version`

**Paso 2: Configurar Git con tu identidad**
```bash
git config --global user.name "Jaziel Anguiano"
git config --global user.email "tu-email-personal@gmail.com"
```

**Paso 3: Instalar Node.js**
- Descargar de nodejs.org (versión LTS, 20.x)
- Instalar con opciones por default
- Verificar: `node --version` y `npm --version`

**Paso 4: Instalar Python 3.11+**
- Descargar de python.org
- ⚠️ IMPORTANTE: en Windows marcar "Add Python to PATH" durante instalación
- Verificar: `python --version` o `python3 --version`

**Paso 5: Instalar GitHub Desktop (opcional pero recomendado)**
- Descargar de desktop.github.com
- Interfaz visual para Git, más fácil al inicio

### Tarea 1.2 — Setup cuenta GitHub (15 min)

- Si no tienes cuenta personal: crear en github.com con tu email personal
- ⚠️ Usar email personal, NO el de Sittek
- Activar autenticación de dos factores (importante)
- Configurar SSH key (opcional, más fácil al inicio usar HTTPS)

### Tarea 1.3 — Cita en SAT para Maira (15 min)

- Entrar a sat.gob.mx → "Citas"
- Agendar cita en SAT Colima para Maira
- Trámite: "Inscripción al RFC con CURP" + activación RESICO PF + Actividad Empresarial
- Llevar día de cita: INE Maira, comprobante domicilio, CURP

---

## DÍA 2 — MARTES (1 hora)

### Tarea 2.1 — Comprar dominios (30 min)

**Paso 1: Comprar koach.mx**
- Ir a Hostinger o Namecheap
- Buscar "koach.mx"
- Si está disponible: comprar 1 año (~$350 MXN)
- Activar protección WHOIS (privacidad)
- ⚠️ Comprar con tarjeta a nombre de Maira (la empresa)

**Paso 2: Comprar koach.app**
- Mismo proveedor
- ~$400 MXN/año
- Tener ambos da más opciones futuras

**Paso 3: Configurar email empresarial**
- Opción A (recomendada): Zoho Mail Free
  - Ir a zoho.com/mail
  - Crear cuenta gratis hasta 5 emails
  - Configurar hola@koach.mx
  - Costo: $0
- Opción B: Google Workspace
  - $130 MXN/mes (más profesional pero costoso)

### Tarea 2.2 — Crear cuenta Meta Business Manager (30 min)

- Ir a business.facebook.com
- Crear cuenta con email hola@koach.mx
- Nombre del negocio: "Koach"
- Completar información básica
- Verificar correo

---

## DÍA 3 — MIÉRCOLES (1 hora)

### Tarea 3.1 — Comprar chip WhatsApp dedicado (30 min)

- Ir a Telcel/AT&T y comprar chip prepago
- Costo: ~$100 MXN
- ⚠️ NO usar tu número personal ni el de Sittek
- Activar chip en cualquier celular (puede ser el de Maira temporalmente)
- Anotar el número
- Recargar saldo mínimo para verificación

### Tarea 3.2 — Conectar número WhatsApp a Meta Business (30 min)

- En Meta Business Manager → Configuración → WhatsApp Accounts
- Agregar número de WhatsApp Business
- Verificar con código SMS al chip nuevo
- ⚠️ El número quedará registrado permanentemente

---

## DÍA 4 — JUEVES (1 hora)

### Tarea 4.1 — Solicitar acceso a WhatsApp Cloud API (30 min)

- En Meta Business Manager → WhatsApp → Plataforma de Cloud API
- Configurar app de desarrollo
- Obtener:
  - Phone Number ID
  - WhatsApp Business Account ID
  - Access Token (válido 24 hrs inicial, después permanente)
- ⚠️ Guardar estos datos en un gestor de contraseñas (1Password, Bitwarden gratis)

### Tarea 4.2 — Setup Supabase (30 min)

- Ir a supabase.com
- Crear cuenta con email hola@koach.mx
- Crear nuevo proyecto: "koach-mvp"
- Región: South America (São Paulo) — más cercano a México
- Anotar:
  - URL del proyecto
  - anon key
  - service role key
- Plan: Free tier (suficiente inicial)

---

## DÍA 5 — VIERNES (1 hora)

### Tarea 5.1 — Maira inicia branding en redes (1 hora con Maira)

**Maira realiza:**

**Paso 1: Crear cuentas oficiales**
- Instagram: @koach.app
- TikTok: @koach.app
- Facebook page: Koach (con URL /koach.app)
- Configurar foto de perfil temporal (placeholder con texto "Koach")
- Bio en cada red:
  > "🚀 Tu coach de salud por WhatsApp
  > 💪 Para mexicanos ocupados
  > 📍 Hecho en Colima, MX
  > 🌐 koach.mx (próximamente)"

**Paso 2: Setup Canva Pro**
- Suscribirse a Canva Pro: $300 MXN/mes o $1,200 MXN/año (recomendado anual)
- Configurar Brand Kit con colores Koach:
  - Verde: #10B981
  - Azul oscuro: #1E293B
  - Acento: #F59E0B
  - Fondo: #FAFAFA

**Paso 3: Contratar diseño de logo**
- Ir a Workana o Fiverr
- Buscar "logo design + flat + minimal"
- Filtrar por reputación (4.8+ estrellas, 50+ reviews)
- Brief:
  > "Logo para Koach, app de coach de salud por WhatsApp para mexicanos.
  > Estilo: moderno, minimal, profesional pero accesible.
  > Paleta: verde #10B981 y azul oscuro #1E293B.
  > Debe funcionar en favicon pequeño y en grande.
  > Entrega: SVG + PNG transparente + variantes monocromático."
- Presupuesto: $800-1,500 MXN
- Tiempo entrega: 3-5 días

**Paso 4: Primer post**
- En Canva: crear post simple con texto
- Texto: "Algo nuevo viene para los mexicanos ocupados que quieren ser más saludables 🚀 #ProximaMente"
- Publicar en las 3 redes

---

## SÁBADO — DÍA 6 (3 horas)

### Bloque 1 — Setup del proyecto local (1 hr)

**Nota (vigente):** el resultado real de este bloque quedó reemplazado por el
scaffold hecho al iniciar el desarrollo real (US-000) — ver estructura final en
`docs/plan-desarrollo-sdd.md` y el `CLAUDE.md` del repo. Se deja el contenido original
solo como referencia de cómo se pensó el arranque.

**Paso 1: Crear estructura de carpetas**

En tu laptop personal, crear:
```
~/proyectos/koach/
```

**Paso 2: Abrir VS Code en esa carpeta**

**Paso 3: Crear estructura inicial (histórica, ya no vigente — ver nota arriba)**

```
koach/
├── README.md
├── .gitignore
├── docs/
│   ├── plan-maestro.md           (pegar plan v6.0)
│   ├── plan-ejecucion.md         (pegar este documento)
│   └── specs/                    (carpeta vacía por ahora)
├── backend/                      (carpeta vacía por ahora)
└── frontend-web/                 (carpeta vacía por ahora)
```

**Paso 4: Crear `.gitignore`**

```
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
venv/

# Environment
.env
.env.local
.env.*.local
*.key

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
.next/
out/

# Logs
*.log
npm-debug.log*

# Misc
.cache/
```

**Paso 5-7:** crear README, repo GitHub, conectar remoto local — ver historial real
del repo (`git log`) para lo que efectivamente se hizo.

### Bloque 2 — Setup página web Next.js (1.5 hrs)

Contenido de referencia sobre cómo se planeó el setup de Next.js/Vercel/dominio —
sigue siendo válido conceptualmente si el sitio de marketing (`koach.mx`) no se ha
iniciado todavía; no es parte del backend de Claude Code.

### Bloque 3 — Setup Supabase inicial (30 min)

**Nota (vigente):** el esquema real completo vive en `docs/plan-maestro.md` sección 14
(30+ tablas). El SQL de ejemplo abajo (solo tabla `users` mínima) es histórico —
no usarlo como base, usar el esquema completo.

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    plan_tier VARCHAR DEFAULT 'free',
    status VARCHAR DEFAULT 'trial'
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own data"
ON users FOR SELECT
USING (auth.uid()::text = id::text);
```

---

## DOMINGO — DÍA 7 (2 horas)

### Bloque 1 — Lista de prospectos beta (1 hr)

**Maira y Jaziel juntos:** crear lista de 30 contactos con nombre, cómo lo conocen,
edad aproximada, probable interés, y mensaje personalizado. Enviar a los primeros 15
por WhatsApp, documentar respuestas.

### Bloque 2 — Empezar primera spec (1 hr)

**Nota (vigente):** el flujo real de trabajo con Claude/Claude Code ya no sigue esta
numeración de specs (US-001 a US-008 aquí) — usar `docs/plan-desarrollo-sdd.md` como
fuente de verdad de las User Stories reales.

---

## ✅ CHECKLIST CIERRE SEMANA 1 (histórico)

- [ ] Git, Node, Python instalados en laptop personal
- [ ] GitHub cuenta personal con repo `koach` privado
- [ ] Cita SAT agendada para Maira
- [ ] Dominio koach.mx comprado
- [ ] Dominio koach.app comprado
- [ ] Email hola@koach.mx funcionando
- [ ] Cuenta Meta Business creada
- [ ] Chip WhatsApp dedicado activo
- [ ] WhatsApp Cloud API tokens obtenidos
- [ ] Supabase proyecto creado con primera tabla
- [ ] Maira: cuentas IG/TikTok/FB creadas
- [ ] Maira: Canva Pro activo
- [ ] Maira: logo en proceso de diseño
- [ ] Maira: primer post publicado en redes
- [ ] Estructura `koach/` creada localmente
- [ ] Next.js inicial deployado en Vercel
- [ ] koach.mx apuntando a Vercel
- [ ] Lista de 30 prospectos hecha
- [ ] 15 mensajes enviados a prospectos
- [ ] Spec 001 escrita y commiteada

**Inversión real semana 1 (cifra original, ver corrección de costos):** ~$2,950 MXN (dominios $750 + chip $100 + Canva $1,200 + logo $900)

---

# 📅 SEMANA 2 — Página web robusta y primeras specs

## 🎯 Objetivo
Tener la página web completa funcional con todas las secciones + 3 specs detalladas listas para implementar en vacaciones.

*(Contenido de referencia sobre construcción de la página web de marketing en Next.js —
Home, Cómo Funciona, Precios, Founders, páginas legales, Sobre Nosotros, FAQ, Contacto,
Header/Footer reutilizables, SEO, formulario de captura de leads. Sigue siendo un plan
razonable para el sitio de marketing `koach.mx`, que es un proyecto aparte del backend
de la app — no bloquea el desarrollo de Claude Code.)*

---

# 📅 SEMANA 3 — Validación y prep para vacaciones

## 🎯 Objetivo
Validar con conocidos, conseguir 5-8 beta confirmados, dejar TODO listo para tu semana intensiva.

*(Contenido de referencia: compartir la web con prospectos, reuniones cortas con
interesados, specs adicionales con numeración histórica no vigente, submit de
templates a Meta, checklist de preparación técnica.)*

---

# 🏖️ SEMANA 4 — VACACIONES INTENSIVAS (40 hrs) — histórico, no vigente

**Nota:** esta semana describe un plan de implementación de 8 User Stories en 5 días,
con una estructura de carpetas y numeración que ya no corresponde a la arquitectura
real (hexagonal, agéntica). Se conserva como referencia de la intención original de
ritmo de desarrollo, no como guía técnica.

---

# 📅 SEMANAS 5-8 — MES 2 — Iteración y primeros usuarios pagando (histórico)

# 📅 SEMANAS 9-12 — MES 3 — Tracción y rentabilidad (histórico)

*(El detalle semana a semana de los meses 2 y 3, incluyendo tareas de producto,
marketing y registro de marca, se conserva sin cambios como plan de referencia de
ritmo operativo — las cifras de usuarios/ingresos siguen el modelo de pricing
original, ver nota de vigencia al inicio del documento sobre el pricing en duda.)*

---

# 💰 PROYECCIÓN FINANCIERA REAL 3 MESES (cifras originales — ver corrección de costos)

| Mes | Usuarios | Ingresos | Costos op | Inversiones | Neto | Acumulado |
|-----|----------|----------|-----------|-------------|------|-----------|
| 1 | 5 beta | $0 | $300 | $3,550 | -$3,850 | -$3,850 |
| 2 | 20 | $2,000 | $1,500 | $7,000 (legal) | -$6,500 | -$10,350 |
| 3 | 30 | $3,500 | $2,500 | $9,850 (marca+) | -$8,850 | -$19,200 |

**De tu bolsillo en 3 meses (cifra original):** ~$3,550 MXN inicial + diferimientos según ingresos.

---

## 🎯 LO MÁS IMPORTANTE — Tres prioridades del trimestre (sigue siendo válido como principio)

1. **MVP funcional primero.** Sin esto, todo lo demás es teoría.
2. **Convertir el primer beta a pago.** La primera transacción valida todo el modelo.
3. **Llegar a usuarios reales pagando de forma sostenida.** Eso es la señal de product-market fit inicial.

Si logras estas 3, el resto es escalamiento.

---

*Koach — Plan de Ejecución Detallado 3 Meses*
*Mayo 2026*
*Cofundadores: Jaziel + Maira Anguiano*
