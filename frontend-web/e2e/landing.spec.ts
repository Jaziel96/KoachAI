import { expect, test } from "@playwright/test";

/**
 * Smoke tests de la landing (US-011).
 *
 * El contenido real (hero, CTA de WhatsApp, FAQ, precios) llega con US-012 —
 * hoy solo existe la página placeholder, así que estos tests cubren lo que
 * SÍ existe: que carga, el idioma/metadata correctos, y los design tokens.
 * No se inventan aserciones sobre contenido que todavía no está.
 */

test("la página carga con 200 y el idioma correcto", async ({ page }) => {
  const response = await page.goto("/");

  expect(response?.status()).toBe(200);
  await expect(page.locator("html")).toHaveAttribute("lang", "es-MX");
});

test("muestra el título y la metadescripción de Koach", async ({ page }) => {
  await page.goto("/");

  await expect(page).toHaveTitle(/Koach/);
  const description = page.locator('meta[name="description"]');
  await expect(description).toHaveAttribute("content", /WhatsApp/);
});

test("el encabezado principal es visible", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Koach", level: 1 })).toBeVisible();
});

test("usa el color primario de marca en el encabezado", async ({ page }) => {
  await page.goto("/");

  const heading = page.getByRole("heading", { name: "Koach", level: 1 });
  // #10b981 (--color-primary) — ver design tokens en globals.css.
  await expect(heading).toHaveCSS("color", "rgb(16, 185, 129)");
});
