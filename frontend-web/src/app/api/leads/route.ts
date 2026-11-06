import { z } from "zod";
import { leadSchema } from "@/lib/leads";

const MAX_BODY_BYTES = 4_000;

export async function POST(request: Request) {
  const raw = await request.text();
  if (raw.length > MAX_BODY_BYTES) {
    return Response.json({ error: "Solicitud demasiado grande" }, { status: 413 });
  }

  let body: unknown;
  try {
    body = JSON.parse(raw);
  } catch {
    return Response.json({ error: "Solicitud inválida" }, { status: 400 });
  }

  // Honeypot: los bots llenan este campo oculto. Respondemos "ok" sin guardar nada.
  if (
    typeof body === "object" &&
    body !== null &&
    typeof (body as { website?: unknown }).website === "string" &&
    (body as { website: string }).website.length > 0
  ) {
    return Response.json({ ok: true });
  }

  const parsed = leadSchema.safeParse(body);
  if (!parsed.success) {
    return Response.json(
      { error: "Revisa los datos", fields: z.flattenError(parsed.error).fieldErrors },
      { status: 400 },
    );
  }

  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  if (!url || !key) {
    return Response.json(
      { error: "El registro no está disponible por ahora" },
      { status: 503 },
    );
  }

  const { email, nombre, meta_principal } = parsed.data;
  try {
    const res = await fetch(`${url.replace(/\/$/, "")}/rest/v1/leads_iniciales?on_conflict=email`, {
      method: "POST",
      headers: {
        apikey: key,
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
        // Email duplicado: se ignora en silencio (CA-2) y se responde igual que un alta nueva.
        Prefer: "resolution=ignore-duplicates,return=minimal",
      },
      body: JSON.stringify({
        email,
        nombre,
        meta_principal,
        consentimiento_at: new Date().toISOString(),
        fuente: "landing",
      }),
    });
    if (!res.ok) {
      return Response.json({ error: "No pudimos guardar tu registro" }, { status: 502 });
    }
  } catch {
    return Response.json({ error: "No pudimos guardar tu registro" }, { status: 502 });
  }

  return Response.json({ ok: true });
}
