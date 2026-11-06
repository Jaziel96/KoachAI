import { expect, test } from "@playwright/test";

/** Páginas legales (US-014). Son borradores pendientes de revisión legal. */

const PAGES = [
  { path: "/privacidad", h1: "Aviso de Privacidad", link: "Aviso de Privacidad" },
  { path: "/terminos", h1: "Términos y Condiciones", link: "Términos y Condiciones" },
  { path: "/disclaimer-medico", h1: "Aviso médico", link: "Aviso médico" },
];

for (const p of PAGES) {
  test.describe(p.path, () => {
    test("carga con título, versión y fecha de actualización (CA-3)", async ({ page }) => {
      const response = await page.goto(p.path);

      expect(response?.status()).toBe(200);
      await expect(page.getByRole("heading", { level: 1 })).toHaveText(p.h1);
      await expect(page.getByText(/Versión 0\.1/)).toBeVisible();
      const time = page.locator("time");
      await expect(time).toHaveAttribute("datetime", "2026-11-06");
      await expect(time).toHaveText("6 de noviembre de 2026");
    });

    test("avisa que es un borrador y no se indexa", async ({ page }) => {
      await page.goto(p.path);

      await expect(page.getByTestId("legal-draft-notice")).toContainText("revisión legal");
      await expect(page.locator('meta[name="robots"]')).toHaveAttribute("content", /noindex/);
      await expect(page.locator('link[rel="canonical"]')).toHaveAttribute(
        "href",
        `https://koach.mx${p.path}`,
      );
    });

    test("la tabla de contenido enlaza a cada sección", async ({ page }) => {
      await page.goto(p.path);

      const toc = page.getByRole("navigation", { name: "Contenido" });
      const hrefs = await toc.locator("a").evaluateAll((as) => as.map((a) => a.getAttribute("href")));
      expect(hrefs.length).toBeGreaterThanOrEqual(5);
      for (const href of hrefs) {
        await expect(page.locator(href!)).toBeAttached();
      }
    });

    test("se llega desde el footer de la landing (CA-1)", async ({ page }) => {
      await page.goto("/");

      await page.getByRole("navigation", { name: "Legal" }).getByRole("link", { name: p.link }).click();
      await expect(page).toHaveURL(new RegExp(`${p.path}$`));
      await expect(page.getByRole("heading", { level: 1 })).toHaveText(p.h1);
    });

    test("no usa lenguaje prohibido por la adenda legal", async ({ page }) => {
      await page.goto(p.path);

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

    test("sin scroll horizontal (responsive)", async ({ page }) => {
      await page.goto(p.path);

      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      );
      expect(overflow).toBeLessThanOrEqual(0);
    });
  });
}

test.describe("elementos obligatorios", () => {
  test("privacidad incluye ARCO, terceros y transferencia internacional (CA-2)", async ({ page }) => {
    await page.goto("/privacidad");

    for (const id of ["responsable", "datos", "finalidad", "consentimiento", "terceros", "transferencia", "arco", "cambios"]) {
      await expect(page.locator(`section#${id}`)).toBeVisible();
    }
    const arco = page.locator("#arco");
    for (const cmd of ["MIS DATOS", "RECTIFICAR", "EXPORTAR MIS DATOS", "BORRAR MIS DATOS"]) {
      await expect(arco).toContainText(cmd);
    }
    await expect(page.locator("#plazos")).toContainText("20 días hábiles");
    await expect(page.locator("#transferencia")).toContainText("Estados Unidos");
  });

  test("términos incluye jurisdicción, aviso de 15 días y mayoría de edad", async ({ page }) => {
    await page.goto("/terminos");

    await expect(page.locator("#jurisdiccion")).toContainText("Colima");
    await expect(page.locator("#modificaciones")).toContainText("15 días");
    await expect(page.locator("#elegibilidad")).toContainText("18 años");
    await expect(page.locator("#servicio")).toContainText("No es un servicio médico");
  });

  test("el aviso médico lista los criterios de derivación", async ({ page }) => {
    await page.goto("/disclaimer-medico");

    const derivacion = page.locator("#derivacion");
    await expect(derivacion.locator("li")).toHaveCount(6);
    await expect(derivacion).toContainText("embarazada");
    await expect(page.locator("#emergencias")).toContainText("911");
  });

  test("los datos aún no definidos se muestran como marcador PENDIENTE", async ({ page }) => {
    await page.goto("/privacidad");

    await expect(page.locator("#responsable")).toContainText("PENDIENTES");
  });
});

test("el FAQ de datos enlaza al Aviso de Privacidad", async ({ page }) => {
  await page.goto("/");

  const item = page.getByTestId("faq-item").filter({ hasText: "¿Qué hacen con mis datos?" });
  await item.locator("summary").click();
  await expect(item.getByRole("link", { name: "Leer el Aviso de Privacidad" })).toHaveAttribute(
    "href",
    "/privacidad",
  );
});
