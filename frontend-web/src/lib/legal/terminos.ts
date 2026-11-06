import { PENDING, type LegalDocument } from "./types";

/**
 * Borrador de Términos y Condiciones (US-014). Cláusulas según
 * analisis-brechas §1.2. El texto final lo redacta un abogado (P-04).
 */
export const terminos: LegalDocument = {
  slug: "terminos",
  title: "Términos y Condiciones",
  description:
    "Las condiciones para usar Koach: qué es el servicio, tus obligaciones y nuestras limitaciones.",
  version: "0.1 (borrador)",
  updatedAt: "2026-11-06",
  sections: [
    {
      id: "servicio",
      title: "Qué es Koach",
      paragraphs: [
        "Koach es un coach de hábitos saludables por WhatsApp que ofrece orientación alimentaria general y acompañamiento. No es un servicio médico ni de nutrición clínica, y no sustituye la consulta con un profesional de la salud.",
      ],
    },
    {
      id: "elegibilidad",
      title: "Quién puede usar Koach",
      paragraphs: [
        "Koach es para personas mayores de 18 años. Si detectamos que eres menor de edad, suspenderemos tu cuenta.",
      ],
    },
    {
      id: "inteligencia-artificial",
      title: "Uso de inteligencia artificial",
      paragraphs: [
        "Las respuestas de Koach las genera un sistema de inteligencia artificial. Puede cometer errores, por lo que debes usar tu criterio y consultar a un profesional ante cualquier duda sobre tu salud.",
      ],
    },
    {
      id: "resultados",
      title: "Sin garantía de resultados",
      paragraphs: [
        "Los resultados son individuales y dependen de muchos factores. Koach no garantiza ningún resultado en tu peso, salud o bienestar.",
      ],
    },
    {
      id: "obligaciones",
      title: "Tus obligaciones",
      items: [
        "Darnos información veraz sobre ti y tu estado de salud.",
        "Consultar a un profesional de la salud si tienes una condición médica, estás embarazada o en lactancia.",
        "No usar Koach para fines ilícitos ni intentar vulnerar su seguridad.",
      ],
    },
    {
      id: "suscripcion",
      title: "Suscripción, pagos y cancelación",
      paragraphs: [
        `${PENDING.precio}`,
        "Puedes cancelar cuando quieras escribiéndole a Koach en el chat.",
      ],
    },
    {
      id: "suspension",
      title: "Suspensión y terminación",
      paragraphs: [
        "Podemos suspender o terminar tu cuenta si incumples estos términos o si detectamos un riesgo para tu seguridad o la de terceros.",
      ],
    },
    {
      id: "responsabilidad",
      title: "Limitación de responsabilidad",
      paragraphs: [
        "En la medida que la ley lo permita, Koach no es responsable por decisiones que tomes con base en la orientación recibida ni por daños indirectos derivados del uso del servicio.",
      ],
    },
    {
      id: "propiedad-intelectual",
      title: "Propiedad intelectual",
      paragraphs: [
        "El contenido, la marca y el software de Koach son propiedad de su titular. No puedes copiarlos ni usarlos sin autorización.",
      ],
    },
    {
      id: "modificaciones",
      title: "Modificaciones",
      paragraphs: [
        "Podemos actualizar estos términos. Te avisaremos con al menos 15 días de anticipación antes de que los cambios surtan efecto.",
      ],
    },
    {
      id: "jurisdiccion",
      title: "Ley aplicable y jurisdicción",
      paragraphs: [
        "Estos términos se rigen por las leyes de México. Para cualquier controversia, las partes se someten a los tribunales competentes de Colima.",
      ],
    },
    {
      id: "contacto",
      title: "Contacto",
      paragraphs: [`Responsable: ${PENDING.responsable}. Correo: ${PENDING.email}.`],
    },
  ],
};
