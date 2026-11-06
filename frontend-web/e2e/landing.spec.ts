import { expect, test } from "@playwright/test";

/**
 * Tests de la landing (US-011 scaffold + US-012 contenido).
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

test("el hero tiene un único h1 con la propuesta de valor", async ({ page }) => {
  await page.goto("/");

  const h1 = page.getByRole("heading", { level: 1 });
  await expect(h1).toHaveCount(1);
  await expect(h1).toContainText("WhatsApp");
});

test("usa el color primario de marca en el acento del h1", async ({ page }) => {
  await page.goto("/");

  // #10b981 (--color-primary) — ver design tokens en globals.css.
  await expect(page.locator("h1 span")).toHaveCSS("color", "rgb(16, 185, 129)");
});

test.describe("secciones", () => {
  for (const id of ["inicio", "problema", "como-funciona", "conversaciones", "precios", "faq"]) {
    test(`existe la sección #${id}`, async ({ page }) => {
      await page.goto("/");
      await expect(page.locator(`section#${id}`)).toBeVisible();
    });
  }

  test("problema tiene 3 puntos y cómo funciona 3 pasos", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("#problema li")).toHaveCount(3);
    await expect(page.locator("#como-funciona li")).toHaveCount(3);
  });

  test("muestra mockups de conversación", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("#conversaciones [role='img']")).toHaveCount(2);
  });

  test("el plan Founder está destacado con su precio", async ({ page }) => {
    await page.goto("/");
    const pricing = page.locator("#precios");
    await expect(pricing).toContainText("Founder");
    await expect(pricing).toContainText("$149");
  });
});

test.describe("CTA de WhatsApp (CA-1)", () => {
  test("todos los CTA abren wa.me con mensaje pre-llenado", async ({ page }) => {
    await page.goto("/");

    const ctas = page.getByTestId("cta-whatsapp");
    expect(await ctas.count()).toBeGreaterThanOrEqual(2);

    for (const cta of await ctas.all()) {
      const href = await cta.getAttribute("href");
      expect(href).toMatch(/^https:\/\/wa\.me\/\d+\?text=/);
      const text = new URL(href!).searchParams.get("text");
      expect(text).toBe("Hola Koach, quiero empezar");
      await expect(cta).toHaveAttribute("target", "_blank");
      await expect(cta).toHaveAttribute("rel", /noopener/);
    }
  });
});

test.describe("FAQ", () => {
  test("tiene 10 preguntas", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("faq-item")).toHaveCount(10);
  });

  test("el acordeón se abre y se cierra al hacer clic", async ({ page }) => {
    await page.goto("/");

    const item = page.getByTestId("faq-item").first();
    await expect(item).not.toHaveAttribute("open", "");

    await item.locator("summary").click();
    await expect(item).toHaveAttribute("open", "");
    await expect(item.locator("p")).toBeVisible();

    await item.locator("summary").click();
    await expect(item).not.toHaveAttribute("open", "");
  });
});

test("el footer enlaza a las páginas legales", async ({ page }) => {
  await page.goto("/");

  const legal = page.getByRole("navigation", { name: "Legal" });
  await expect(legal.locator('a[href="/privacidad"]')).toBeVisible();
  await expect(legal.locator('a[href="/terminos"]')).toBeVisible();
  await expect(legal.locator('a[href="/disclaimer-medico"]')).toBeVisible();
});

test.describe("SEO y Open Graph (CA-3)", () => {
  test("define canonical, og y twitter", async ({ page }) => {
    await page.goto("/");

    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", "https://koach.mx");
    await expect(page.locator('meta[property="og:title"]')).toHaveAttribute("content", /Koach/);
    await expect(page.locator('meta[property="og:description"]')).toHaveAttribute("content", /WhatsApp/);
    await expect(page.locator('meta[property="og:locale"]')).toHaveAttribute("content", "es_MX");
    await expect(page.locator('meta[property="og:image"]')).toHaveAttribute("content", /opengraph-image/);
    await expect(page.locator('meta[name="twitter:card"]')).toHaveAttribute("content", "summary_large_image");
  });

  test("la imagen Open Graph se sirve como PNG", async ({ page, request }) => {
    await page.goto("/");
    const src = await page.locator('meta[property="og:image"]').getAttribute("content");
    const res = await request.get(new URL(src!).pathname);
    expect(res.status()).toBe(200);
    expect(res.headers()["content-type"]).toContain("image/png");
  });
});

test("el copy no usa lenguaje prohibido por la adenda legal", async ({ page }) => {
  await page.goto("/");

  const text = await page.locator("body").innerText();
  for (const banned of [
    /plan nutricional/i,
    /\bdietas?\b/i,
    /tratamiento/i,
    /diagn[óo]stic/i,
    /nutri[óo]logo virtual/i,
  ]) {
    expect(text).not.toMatch(banned);
  }
});

test("responsive: sin scroll horizontal y CTA visible y tocable (CA-2)", async ({ page }) => {
  await page.goto("/");

  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(0);

  const cta = page.getByTestId("cta-whatsapp").first();
  await expect(cta).toBeVisible();
  const box = await cta.boundingBox();
  expect(box!.height).toBeGreaterThanOrEqual(44);
});
