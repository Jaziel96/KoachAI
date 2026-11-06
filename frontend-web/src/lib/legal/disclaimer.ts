import type { LegalDocument } from "./types";

/**
 * Borrador del aviso médico (US-014). Criterios de derivación según
 * adenda-legal-pendientes §1.5.
 */
export const disclaimer: LegalDocument = {
  slug: "disclaimer-medico",
  title: "Aviso médico",
  description:
    "Qué es y qué no es Koach, y cuándo te recomendaremos acudir con un profesional de la salud.",
  version: "0.1 (borrador)",
  updatedAt: "2026-11-06",
  sections: [
    {
      id: "que-es",
      title: "Qué es Koach",
      paragraphs: [
        "Koach es un coach de hábitos saludables que ofrece orientación alimentaria general y acompañamiento, con base en los criterios de la NOM-043-SSA2-2012.",
      ],
    },
    {
      id: "que-no-es",
      title: "Qué no es Koach",
      items: [
        "No es un servicio médico ni de nutrición clínica.",
        "No sustituye la consulta con un médico o un nutriólogo.",
        "No receta medicamentos ni da indicaciones alimentarias para condiciones de salud.",
        "No atiende urgencias médicas ni emocionales.",
      ],
    },
    {
      id: "derivacion",
      title: "Cuándo te recomendaremos acudir con un profesional",
      paragraphs: [
        "Koach te recomendará consultar a un profesional de la salud, y no te dará orientación alimentaria, si te encuentras en alguno de estos casos:",
      ],
      items: [
        "Tu índice de masa corporal está por debajo de 18.5 o es de 30 o más.",
        "Estás embarazada o en lactancia.",
        "Tienes diabetes o hipertensión.",
        "Detectamos señales de un trastorno de la conducta alimentaria.",
        "Eres menor de 18 años.",
        "Tienes más de 70 años (en ese caso, con supervisión profesional).",
      ],
    },
    {
      id: "emergencias",
      title: "En caso de emergencia",
      paragraphs: [
        "Si tú o alguien más está en peligro, llama al 911 o acude al servicio de urgencias más cercano. Koach no puede atender emergencias.",
      ],
    },
    {
      id: "resultados",
      title: "Resultados individuales",
      paragraphs: [
        "Los resultados varían de persona a persona. Koach no garantiza ningún resultado en tu salud ni en tu peso.",
      ],
    },
  ],
};
