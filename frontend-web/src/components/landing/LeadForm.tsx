"use client";

import { useState, type FormEvent } from "react";
import { GOALS, leadSchema, type LeadFieldErrors } from "@/lib/leads";

type Status = "idle" | "submitting" | "success" | "error";

const inputClass =
  "mt-1 min-h-12 w-full rounded-xl border border-dark/20 bg-white px-4 py-3 text-base focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-dark";

export function LeadForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [errors, setErrors] = useState<LeadFieldErrors>({});
  const [message, setMessage] = useState("");

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const payload = {
      email: String(form.get("email") ?? ""),
      nombre: String(form.get("nombre") ?? ""),
      meta_principal: String(form.get("meta_principal") ?? ""),
      consentimiento: form.get("consentimiento") === "on",
      website: String(form.get("website") ?? ""),
    };

    const check = leadSchema.safeParse(payload);
    if (!check.success) {
      const fields: LeadFieldErrors = {};
      for (const issue of check.error.issues) {
        const key = issue.path[0] as keyof LeadFieldErrors;
        (fields[key] ??= []).push(issue.message);
      }
      setErrors(fields);
      setStatus("idle");
      setMessage("");
      return;
    }

    setErrors({});
    setStatus("submitting");
    setMessage("");
    try {
      const res = await fetch("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setStatus("success");
        return;
      }
      const data = (await res.json().catch(() => ({}))) as {
        error?: string;
        fields?: LeadFieldErrors;
      };
      if (res.status === 400 && data.fields) setErrors(data.fields);
      setMessage(data.error ?? "No pudimos guardar tu registro. Inténtalo de nuevo.");
      setStatus("error");
    } catch {
      setMessage("No pudimos conectarnos. Revisa tu conexión e inténtalo de nuevo.");
      setStatus("error");
    }
  }

  if (status === "success") {
    return (
      <p
        role="status"
        data-testid="lead-success"
        className="mx-auto max-w-md rounded-2xl bg-white p-6 text-center text-lg font-semibold shadow-sm ring-2 ring-primary"
      >
        ¡Listo! Te avisaremos cuando Koach esté disponible.
      </p>
    );
  }

  return (
    <form
      onSubmit={onSubmit}
      noValidate
      data-testid="lead-form"
      className="mx-auto flex max-w-md flex-col gap-4 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-dark/10"
    >
      <div>
        <label htmlFor="lead-nombre" className="font-semibold">
          Nombre
        </label>
        <input
          id="lead-nombre"
          name="nombre"
          autoComplete="given-name"
          aria-invalid={!!errors.nombre}
          aria-describedby={errors.nombre ? "lead-nombre-error" : undefined}
          className={inputClass}
        />
        {errors.nombre && (
          <p id="lead-nombre-error" className="mt-1 text-sm text-red-700">
            {errors.nombre[0]}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="lead-email" className="font-semibold">
          Correo
        </label>
        <input
          id="lead-email"
          name="email"
          type="email"
          autoComplete="email"
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? "lead-email-error" : undefined}
          className={inputClass}
        />
        {errors.email && (
          <p id="lead-email-error" className="mt-1 text-sm text-red-700">
            {errors.email[0]}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="lead-meta" className="font-semibold">
          Tu meta principal
        </label>
        <select
          id="lead-meta"
          name="meta_principal"
          defaultValue=""
          aria-invalid={!!errors.meta_principal}
          aria-describedby={errors.meta_principal ? "lead-meta-error" : undefined}
          className={inputClass}
        >
          <option value="" disabled>
            Elige una opción
          </option>
          {GOALS.map((g) => (
            <option key={g.value} value={g.value}>
              {g.label}
            </option>
          ))}
        </select>
        {errors.meta_principal && (
          <p id="lead-meta-error" className="mt-1 text-sm text-red-700">
            {errors.meta_principal[0]}
          </p>
        )}
      </div>

      {/* Honeypot: invisible para personas, los bots lo llenan. */}
      <div aria-hidden="true" className="absolute -left-[9999px] h-0 w-0 overflow-hidden">
        <label htmlFor="lead-website">Sitio web</label>
        <input id="lead-website" name="website" tabIndex={-1} autoComplete="off" />
      </div>

      <div>
        <label className="flex items-start gap-3 text-sm">
          <input
            type="checkbox"
            name="consentimiento"
            aria-invalid={!!errors.consentimiento}
            className="mt-1 h-5 w-5 shrink-0"
          />
          <span>
            Acepto el{" "}
            <a href="/privacidad" className="font-semibold underline underline-offset-4">
              Aviso de Privacidad
            </a>{" "}
            para recibir un aviso cuando Koach esté disponible.
          </span>
        </label>
        {errors.consentimiento && (
          <p className="mt-1 text-sm text-red-700">{errors.consentimiento[0]}</p>
        )}
      </div>

      {status === "error" && (
        <p role="alert" data-testid="lead-error" className="rounded-xl bg-red-50 p-3 text-sm text-red-800">
          {message}
        </p>
      )}

      <button
        type="submit"
        disabled={status === "submitting"}
        className="inline-flex min-h-12 items-center justify-center rounded-full bg-primary px-6 py-3 text-base font-semibold text-dark transition hover:brightness-95 disabled:opacity-60"
      >
        {status === "submitting" ? "Enviando…" : "Avísame"}
      </button>
    </form>
  );
}
