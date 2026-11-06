import { z } from "zod";

/** Metas disponibles en el formulario de lista de espera (US-013). */
export const GOALS = [
  { value: "bajar_peso", label: "Bajar de peso" },
  { value: "ganar_musculo", label: "Ganar músculo" },
  { value: "comer_mejor", label: "Comer mejor" },
  { value: "mas_energia", label: "Tener más energía" },
  { value: "otra", label: "Otra" },
] as const;

const goalValues = GOALS.map((g) => g.value) as [
  (typeof GOALS)[number]["value"],
  ...(typeof GOALS)[number]["value"][],
];

/** Esquema compartido: lo usan el formulario (cliente) y la API (servidor). */
export const leadSchema = z.object({
  email: z
    .string()
    .trim()
    .toLowerCase()
    .max(254, "El correo es demasiado largo")
    .pipe(z.email("Escribe un correo válido")),
  nombre: z.string().trim().min(1, "Escribe tu nombre").max(100, "El nombre es demasiado largo"),
  meta_principal: z.enum(goalValues, "Elige una meta"),
  consentimiento: z.literal(true, "Debes aceptar el Aviso de Privacidad"),
});

export type LeadInput = z.infer<typeof leadSchema>;
export type LeadFieldErrors = Partial<Record<keyof LeadInput, string[]>>;
