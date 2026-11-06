export type LegalSection = {
  id: string;
  title: string;
  paragraphs?: string[];
  items?: string[];
};

export type LegalDocument = {
  slug: "privacidad" | "terminos" | "disclaimer-medico";
  title: string;
  description: string;
  /** Versión del documento; se incrementa en cada cambio de fondo. */
  version: string;
  /** Fecha ISO (YYYY-MM-DD) de la última actualización. */
  updatedAt: string;
  sections: LegalSection[];
};

/** Marcadores visibles de datos que aún no están definidos (no se inventan). */
export const PENDING = {
  responsable: "[RESPONSABLE Y DOMICILIO PENDIENTES]",
  email: "[CORREO DE CONTACTO PENDIENTE]",
  precio: "[CONDICIONES DE PRECIO Y RENOVACIÓN PENDIENTES]",
} as const;

export function formatLegalDate(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  return new Intl.DateTimeFormat("es-MX", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(Date.UTC(y, m - 1, d)));
}
