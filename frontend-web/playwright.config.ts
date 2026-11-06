import { defineConfig, devices } from "@playwright/test";

/**
 * Configuración de Playwright para los E2E de la landing (US-011).
 *
 * Corre contra un build de producción (`next build && next start`), no
 * `next dev`: así se prueba lo mismo que termina en Vercel, no el modo
 * desarrollo (que tiene overlays y comportamiento distinto).
 */
// E2E_PORT permite evitar un servidor viejo ocupando el 3000 (reuseExistingServer).
const PORT = process.env.E2E_PORT ?? "3000";
const MOCK_PORT = process.env.E2E_MOCK_PORT ?? "3101";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: "list",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    // CA-2 (US-012): >90% del tráfico es móvil.
    { name: "mobile-chrome", use: { ...devices["Pixel 7"] } },
    { name: "mobile-safari", use: { ...devices["iPhone 14"] } },
  ],
  webServer: [
    {
      // Supabase falso para US-013 (nunca se usa una base real en los E2E).
      command: "node e2e/mock-supabase.mjs",
      url: `http://127.0.0.1:${MOCK_PORT}`,
      env: { E2E_MOCK_PORT: MOCK_PORT },
      reuseExistingServer: !process.env.CI,
    },
    {
      command: `npm run build && npm run start -- -p ${PORT}`,
      url: `http://127.0.0.1:${PORT}`,
      env: {
        SUPABASE_URL: `http://127.0.0.1:${MOCK_PORT}`,
        SUPABASE_SERVICE_KEY: "test-service-key",
      },
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
});
