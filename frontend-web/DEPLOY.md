# Deploy a Vercel (US-011)

> ⏸️ **PAUSADO — 27 sep 2026.** Retomar aquí:
> - ✅ Código listo en la rama `feature/US-011-landing-setup`: Next.js 16 +
>   Tailwind 4 + tokens de Koach; `npm run build` y `npm run lint` pasan.
>   **Debe estar integrado a `master` antes del deploy** (Vercel despliega
>   desde el repo `https://github.com/Jaziel96/KoachAI`).
> - ✅ **CA-2** medido en local (build de producción, Lighthouse móvil
>   por defecto): Performance **99** (LCP 2.2 s, TBT 50 ms, CLS 0).
>   Volver a medir sobre koach.mx ya desplegado.
> - ⏳ **Pendiente (lo haces tú):** todos los pasos de abajo. Nada del deploy
>   ni del DNS está hecho.
> - ⏳ **CA-1** (koach.mx con HTTPS) y **CA-3** (deploy automático en push)
>   **no están verificados** — solo se pueden comprobar al terminar el paso 5.

Pasos manuales — requieren tu cuenta de Vercel y el acceso al DNS de
`koach.mx`; no se pueden automatizar desde el repo.

## Nota de versiones

La spec (RF-1) decía Next.js 14. Se usó **Next.js 16 + Tailwind 4** por ser
lo vigente. En Tailwind 4 los tokens viven en `src/app/globals.css` (bloque
`@theme`), no en `tailwind.config.js`.

## 1. Crear el proyecto en Vercel

1. https://vercel.com → **Add New… → Project** → **Import Git Repository** →
   `Jaziel96/KoachAI` (si no aparece, autoriza la app de GitHub para ese repo).
2. En la pantalla de configuración:
   - **Root Directory**: `frontend-web` (monorepo — sin esto Vercel no
     encuentra `package.json`).
   - **Framework Preset**: Next.js (se detecta solo).
   - Build/Install/Output: dejar los valores por defecto.
   - **Node.js Version**: 20.x o superior (Settings → General).
3. **Deploy**. Al terminar tendrás una URL `*.vercel.app`; ábrela y confirma
   que se ve "Koach — Muy pronto".

## 2. Rama de producción

**Settings → Git → Production Branch**: `master`. Cada push a `master` será
un deploy de producción y cada rama/PR un preview (esto es lo que cubre CA-3).

## 3. Agregar el dominio

**Settings → Domains → Add**: `koach.mx` y `www.koach.mx` (deja que `www`
redirija al dominio principal).

## 4. DNS de koach.mx

En el panel de tu registrador/DNS, crea los registros **exactamente como los
muestra Vercel en Settings → Domains** (Vercel indica el valor correcto por
proyecto). Normalmente son:

| Tipo | Nombre | Valor |
|---|---|---|
| A | `@` | `76.76.21.21` |
| CNAME | `www` | `cname.vercel-dns.com` |

Si el dominio ya tenía otros registros A/CNAME para `@` o `www`, bórralos
primero. La propagación puede tardar de minutos a unas horas.

## 5. Verificación (aquí se cierran CA-1 y CA-3)

- [ ] **CA-1**: `https://koach.mx` carga con candado HTTPS (Vercel emite el
      certificado solo cuando el DNS ya resuelve; el estado en Domains debe
      decir *Valid Configuration*).
- [ ] **CA-3**: haz un cambio trivial (p. ej. el texto de `src/app/page.tsx`),
      push a `master` y confirma que aparece un deployment nuevo en Vercel
      sin intervención manual.
- [ ] **CA-2**: en Chrome DevTools → Lighthouse sobre `https://koach.mx`,
      Performance > 90.

## Desarrollo local

```bash
cd frontend-web
npm install
npm run dev      # http://localhost:3000
npm run build && npm start   # build de producción
```
