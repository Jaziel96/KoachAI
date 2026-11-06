/** Número de respaldo si no hay variable de entorno — es un placeholder, no un número real. */
export const PLACEHOLDER_WHATSAPP_NUMBER = "5215500000000";

export const WHATSAPP_PREFILLED_MESSAGE = "Hola Koach, quiero empezar";

/** Deja solo dígitos: tolera "+52 1 55 ..." en la variable de entorno. */
function sanitizeNumber(raw: string | undefined): string {
  const digits = (raw ?? "").replace(/\D/g, "");
  return digits.length > 0 ? digits : PLACEHOLDER_WHATSAPP_NUMBER;
}

export function buildWhatsappUrl(
  number: string | undefined = process.env.NEXT_PUBLIC_WHATSAPP_NUMBER,
  message: string = WHATSAPP_PREFILLED_MESSAGE,
): string {
  return `https://wa.me/${sanitizeNumber(number)}?text=${encodeURIComponent(message)}`;
}
