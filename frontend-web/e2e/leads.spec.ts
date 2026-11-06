import { expect, test, type Page } from "@playwright/test";

/** Captura de leads (US-013). El servidor habla con un Supabase falso (mock-supabase.mjs). */

const MOCK = `http://127.0.0.1:${process.env.E2E_MOCK_PORT ?? 3101}`;

type Lead = { email: string; nombre: string; meta_principal: string; consentimiento_at: string; fuente: string };

async function savedLeads(request: import("@playwright/test").APIRequestContext): Promise<Lead[]> {
  return (await request.get(`${MOCK}/__leads`)).json();
}

function uniqueEmail(tag: string) {
  return `${tag}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`;
}

async function fillForm(page: Page, email: string, nombre = "Ana") {
  await page.getByLabel("Nombre").fill(nombre);
  await page.getByLabel("Correo").fill(email);
  await page.getByLabel("Tu meta principal").selectOption("comer_mejor");
  await page.getByRole("checkbox").check();
}

test.describe("formulario de lista de espera", () => {
  test("existe la sección con sus campos", async ({ page }) => {
    await page.goto("/");

    const section = page.locator("section#lista-espera");
    await expect(section).toBeVisible();
    await expect(section.getByLabel("Nombre")).toBeVisible();
    await expect(section.getByLabel("Correo")).toBeVisible();
    await expect(section.getByLabel("Tu meta principal")).toBeVisible();
    await expect(section.getByRole("link", { name: "Aviso de Privacidad" })).toHaveAttribute(
      "href",
      "/privacidad",
    );
  });

  test("guarda el lead en la base y confirma visualmente (CA-1, RF-4)", async ({ page, request }) => {
    const email = uniqueEmail("alta");
    await page.goto("/");
    await fillForm(page, email.toUpperCase());
    await page.getByRole("button", { name: "Avísame" }).click();

    await expect(page.getByTestId("lead-success")).toContainText("Te avisaremos");

    const saved = (await savedLeads(request)).filter((l) => l.email === email);
    expect(saved).toHaveLength(1);
    expect(saved[0]).toMatchObject({ nombre: "Ana", meta_principal: "comer_mejor", fuente: "landing" });
    expect(saved[0].consentimiento_at).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  });

  test("un email duplicado no crea un registro nuevo (CA-2)", async ({ page, request }) => {
    const email = uniqueEmail("dup");
    for (let i = 0; i < 2; i++) {
      await page.goto("/");
      await fillForm(page, email, i === 0 ? "Ana" : "Ana Otra Vez");
      await page.getByRole("button", { name: "Avísame" }).click();
      // Ambas veces el usuario ve la misma confirmación: no se revela si ya existía.
      await expect(page.getByTestId("lead-success")).toBeVisible();
    }

    expect((await savedLeads(request)).filter((l) => l.email === email)).toHaveLength(1);
  });

  test("valida los campos antes de enviar", async ({ page }) => {
    const posts: string[] = [];
    page.on("request", (r) => r.method() === "POST" && posts.push(r.url()));
    await page.goto("/");

    await page.getByRole("button", { name: "Avísame" }).click();
    await expect(page.getByText("Escribe tu nombre")).toBeVisible();
    await expect(page.getByText("Escribe un correo válido")).toBeVisible();
    await expect(page.getByText("Elige una meta")).toBeVisible();
    await expect(page.getByText("Debes aceptar el Aviso de Privacidad")).toBeVisible();

    await page.getByLabel("Correo").fill("no-es-un-correo");
    await page.getByRole("button", { name: "Avísame" }).click();
    await expect(page.getByText("Escribe un correo válido")).toBeVisible();

    // La validación del cliente frena el envío: no sale ninguna petición a la API.
    expect(posts).toHaveLength(0);
  });

  test("un error de red muestra un mensaje claro y permite reintentar (CA-3)", async ({ page }) => {
    await page.route("**/api/leads", (route) => route.abort("failed"));
    await page.goto("/");
    await fillForm(page, uniqueEmail("red"));
    await page.getByRole("button", { name: "Avísame" }).click();

    await expect(page.getByTestId("lead-error")).toContainText("Revisa tu conexión");
    // Sigue el formulario con los datos, listo para reintentar.
    await expect(page.getByLabel("Nombre")).toHaveValue("Ana");
    await expect(page.getByRole("button", { name: "Avísame" })).toBeEnabled();
  });

  test("un fallo del servidor muestra un mensaje claro (CA-3)", async ({ page }) => {
    await page.route("**/api/leads", (route) =>
      route.fulfill({ status: 502, json: { error: "No pudimos guardar tu registro" } }),
    );
    await page.goto("/");
    await fillForm(page, uniqueEmail("502"));
    await page.getByRole("button", { name: "Avísame" }).click();

    await expect(page.getByTestId("lead-error")).toContainText("No pudimos guardar tu registro");
  });
});

test.describe("POST /api/leads", () => {
  const valid = {
    nombre: "Ana",
    meta_principal: "otra",
    consentimiento: true,
  };

  test("rechaza datos inválidos con 400 y detalle por campo", async ({ request }) => {
    const res = await request.post("/api/leads", {
      data: { ...valid, email: "malo", meta_principal: "volar" },
    });

    expect(res.status()).toBe(400);
    const body = await res.json();
    expect(body.fields.email).toBeDefined();
    expect(body.fields.meta_principal).toBeDefined();
  });

  test("exige consentimiento", async ({ request }) => {
    const res = await request.post("/api/leads", {
      data: { ...valid, email: uniqueEmail("sin-consent"), consentimiento: false },
    });

    expect(res.status()).toBe(400);
    expect((await res.json()).fields.consentimiento).toBeDefined();
  });

  test("rechaza JSON roto y cuerpos enormes", async ({ request }) => {
    const bad = await request.post("/api/leads", {
      headers: { "Content-Type": "application/json" },
      data: "{no es json",
    });
    expect(bad.status()).toBe(400);

    const big = await request.post("/api/leads", {
      data: { ...valid, email: uniqueEmail("big"), nombre: "x".repeat(10_000) },
    });
    expect(big.status()).toBe(413);
  });

  test("el honeypot responde ok pero no guarda nada", async ({ request }) => {
    const email = uniqueEmail("bot");
    const res = await request.post("/api/leads", {
      data: { ...valid, email, website: "http://spam.example" },
    });

    expect(res.status()).toBe(200);
    expect((await savedLeads(request)).filter((l) => l.email === email)).toHaveLength(0);
  });
});
