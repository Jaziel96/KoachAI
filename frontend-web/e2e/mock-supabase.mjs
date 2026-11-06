// Supabase falso (PostgREST) para los E2E de US-013: nunca se toca una base real.
// POST /rest/v1/leads_iniciales  → guarda (ignora duplicados por email si Prefer lo pide).
// GET  /__leads                  → lista lo guardado, para que los tests lo inspeccionen.
import http from "node:http";

const PORT = Number(process.env.E2E_MOCK_PORT ?? 3101);
const KEY = "test-service-key";
const leads = [];

http
  .createServer((req, res) => {
    const send = (status, body) => {
      res.writeHead(status, { "Content-Type": "application/json" });
      res.end(body === undefined ? "" : JSON.stringify(body));
    };

    if (req.method === "GET" && req.url === "/__leads") return send(200, leads);
    if (req.method === "GET" && req.url === "/") return send(200, { ok: true });

    if (req.method === "POST" && req.url?.startsWith("/rest/v1/leads_iniciales")) {
      if (req.headers.apikey !== KEY) return send(401, { message: "Invalid API key" });
      let raw = "";
      req.on("data", (c) => (raw += c));
      req.on("end", () => {
        const row = JSON.parse(raw);
        const ignore = String(req.headers.prefer ?? "").includes("ignore-duplicates");
        const exists = leads.some((l) => l.email === row.email);
        if (exists && !ignore) return send(409, { code: "23505" });
        if (!exists) leads.push(row);
        send(201);
      });
      return;
    }
    send(404, { message: "not found" });
  })
  .listen(PORT, "127.0.0.1");
