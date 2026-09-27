# Deploy a Railway (US-004)

> ⏸️ **PAUSADO — 27 sep 2026.** Retomar aquí:
> - ✅ Repo GitHub listo: `https://github.com/Jaziel96/KoachAI` (push forzado,
>   reemplazó un intento anterior — ver commit `db7135b` en adelante).
> - ✅ Proyecto Railway ya creado: nombre **`exquisite-hope`**
>   (`railway.com/project/7b921bca-134b-4d1c-a782-398150bcb7e2`), ambiente
>   `production`. Está **vacío** — el canvas del proyecto no tiene ningún
>   servicio todavía.
> - ⏳ **Siguiente paso pendiente**: en el canvas del proyecto (ícono de
>   árbol/nodos en la barra lateral, no el de engranaje ⚙️) → **"+ New"** →
>   **"GitHub Repo"** → seleccionar `Jaziel96/KoachAI`. Eso crea la tarjeta del
>   servicio. Luego click en esa tarjeta para llegar a sus pestañas
>   (Deployments/Variables/Settings) y continuar desde el **paso 2** de abajo
>   (Root Directory = `backend`, Redis, variables, dominio).
> - El repo ya tiene todo lo necesario (`backend/nixpacks.toml` con el start
>   command que corre migraciones); no hace falta tocar código, solo
>   configuración en el dashboard de Railway.

Pasos manuales — requieren tu cuenta de GitHub y Railway, no se pueden
automatizar desde aquí.

## 1. Repo en GitHub

✅ Ya hecho — `https://github.com/Jaziel96/KoachAI`, rama `master`.

## 2. Crear el proyecto en Railway

1. https://railway.app → **New Project** → **Deploy from GitHub repo** → selecciona `koach`.
2. En el servicio creado, ve a **Settings**:
   - **Root Directory**: `backend` (el repo es un monorepo — sin esto Railway
     intenta hacer build desde la raíz y no va a encontrar `pyproject.toml`).
   - **Watch Paths**: `backend/**` (opcional — evita redeploys cuando solo
     cambias `frontend-web/` o `docs/`).
3. Railway detecta Nixpacks automáticamente y usa `backend/nixpacks.toml`
   (ya en el repo) para el build y el start command — incluye
   `alembic upgrade head` antes de levantar uvicorn (CA-4).

## 3. Provisionar Redis

En el proyecto de Railway: **+ New** → **Database** → **Add Redis**.
Railway expone `REDIS_URL` automáticamente como variable — solo falta
referenciarla en el servicio del backend (paso 4).

## 4. Variables de entorno

En **Settings → Variables** del servicio backend, agrega (usa **Variable
Reference** de Railway para `REDIS_URL` del addon en vez de copiarla a mano):

| Variable | Valor |
|---|---|
| `APP_NAME` | `Koach` |
| `ENVIRONMENT` | `prod` |
| `DEBUG` | `false` |
| `DATABASE_URL` | connection string de Supabase (pooler, modo `asyncpg`) |
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_SERVICE_KEY` | service role key de Supabase |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` (referencia al addon del paso 3) |
| `AI_STRATEGY` | `api` |
| `AI_SMART_PROVIDER` | `anthropic` |
| `AI_FAST_PROVIDER` | `gemini` |
| `ANTHROPIC_API_KEY` | tu key real |
| `GEMINI_API_KEY` | tu key real |
| `WHATSAPP_TOKEN` | tu token real |
| `WHATSAPP_PHONE_NUMBER_ID` | tu phone number id real |
| `WHATSAPP_VERIFY_TOKEN` | el verify token que configuraste en Meta |
| `CORS_ALLOWED_ORIGINS` | `["https://app.koach.mx"]` (o el dominio real de la landing/app) |

**Nunca** pegues estos valores en un commit ni en el chat — solo en el
dashboard de Railway.

## 5. Dominio HTTPS

**Settings → Networking → Generate Domain** genera un dominio
`*.up.railway.app` con HTTPS automático (CA-2). Un dominio propio
(`api.koach.mx`) se puede apuntar después con un CNAME, aquí mismo.

## 6. Verificar

- CA-1: haz un commit y push a `master` (o `main`, según cómo lo hayas
  llamado en GitHub) — Railway debe iniciar el deploy solo, visible en la
  pestaña **Deployments**.
- CA-2: `curl https://<tu-dominio>.up.railway.app/health` debe responder
  `200` (o `503` si algo está mal — el propio endpoint lo dice en `checks`).
- CA-3: pestaña **Deployments → View Logs** debe mostrar los logs JSON
  (`structlog`) de cada request.
- CA-4: el log de build/deploy debe mostrar la línea de
  `alembic upgrade head` corriendo antes de que arranque uvicorn.

Avísame cuando tengas el repo en GitHub y el proyecto creado en Railway —
verificamos los 4 CA juntos con el dominio real.
