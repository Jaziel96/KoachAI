/**
 * Copy de la landing (US-012).
 *
 * Lenguaje obligatorio (docs/adenda-legal-pendientes.md §1.6): "orientación
 * alimentaria", "acompañamiento", "coach de hábitos saludables". Nunca
 * "plan nutricional", "dieta" como prescripción, "tratamiento", "diagnóstico"
 * ni "nutriólogo virtual". Hay un test E2E que lo vigila.
 */

export const PROBLEMS = [
  {
    title: "Los planes rígidos se rompen al primer antojo",
    body: "Un menú fijo no sabe que hoy hubo junta, tráfico y tortas. Cuando algo cambia, lo dejas.",
  },
  {
    title: "Una app más que se te olvida abrir",
    body: "Si tienes que acordarte de registrar todo, tarde o temprano ya no lo haces.",
  },
  {
    title: "No cocinan lo que tú tienes en casa",
    body: "Las recomendaciones genéricas olvidan tu alacena, tu presupuesto y la comida mexicana de todos los días.",
  },
] as const;

export const STEPS = [
  {
    title: "Escríbele por WhatsApp",
    body: "Sin descargar nada. Abres el chat y saludas.",
  },
  {
    title: "Cuéntale de ti y de tu alacena",
    body: "Tu meta, tus hábitos y lo que tienes en casa. Koach arma su orientación con eso.",
  },
  {
    title: "Recibe acompañamiento cada día",
    body: "Koach te escribe primero: te propone opciones para comer y te ayuda a mantener tus hábitos.",
  },
] as const;

export type ChatMessage = { from: "user" | "koach"; text: string };

export const CHATS: { title: string; messages: ChatMessage[] }[] = [
  {
    title: "Cuando no sabes qué cenar",
    messages: [
      { from: "user", text: "Hoy no sé qué cenar. Tengo huevo, frijoles y tortillas 🥚" },
      {
        from: "koach",
        text: "¡Con eso sale bien! Te propongo 3 opciones:\n1️⃣ Huevo a la mexicana con frijoles\n2️⃣ Molletes con huevo\n3️⃣ Tacos de frijol con huevo\n¿Cuál se te antoja?",
      },
      { from: "user", text: "Los molletes 😋" },
    ],
  },
  {
    title: "Cuando te saliste del camino",
    messages: [
      { from: "user", text: "Me comí unas tortas en la comida 😅" },
      {
        from: "koach",
        text: "Una comida no echa a perder tu semana. Para la cena, ¿te late algo ligero con verduras, o prefieres que lo veamos mañana con calma?",
      },
    ],
  },
];

export const FOUNDER_BENEFITS = [
  "Precio congelado de por vida",
  "Acceso anticipado a todo lo nuevo",
  "Voto mensual sobre qué se construye",
  "Insignia Founder permanente",
  "Canal privado con los cofundadores",
] as const;

export type FaqItem = {
  question: string;
  answer: string;
  link?: { href: string; label: string };
};

export const FAQ: FaqItem[] = [
  {
    question: "¿Qué es Koach?",
    answer:
      "Koach es un coach de hábitos saludables que vive en tu WhatsApp. Te da orientación alimentaria general y te acompaña día a día para que mantengas tus hábitos.",
  },
  {
    question: "¿Koach es un servicio médico o de nutrición?",
    answer:
      "No. Koach ofrece orientación alimentaria y acompañamiento de hábitos. No sustituye la consulta con un médico o un nutriólogo.",
  },
  {
    question: "¿Cómo funciona?",
    answer:
      "Le escribes por WhatsApp, le cuentas tu meta y lo que tienes en casa, y Koach te propone opciones y te escribe para acompañarte durante el día.",
  },
  {
    question: "¿Necesito instalar una app?",
    answer:
      "No. Koach funciona dentro de WhatsApp, la app que ya usas todos los días.",
  },
  {
    question: "¿Qué pasa si tengo una condición de salud?",
    answer:
      "Koach solo da orientación alimentaria general. Si nos cuentas que tienes una condición como diabetes o hipertensión, o que estás embarazada o en lactancia, te recomendará acudir con un profesional de la salud.",
  },
  {
    question: "¿Me va a prohibir comidas?",
    answer:
      "No. Koach nunca te prohíbe alimentos. Te propone hasta 3 opciones, parte de lo que ya tienes en casa y tú decides.",
  },
  {
    question: "¿Cuánto cuesta?",
    answer:
      "El plan Founder cuesta $149 MXN al mes, con precio congelado de por vida para los primeros 50 usuarios.",
  },
  {
    question: "¿Qué hacen con mis datos?",
    answer:
      "Usamos tu información solo para acompañarte, conforme a nuestro Aviso de Privacidad.",
    link: { href: "/privacidad", label: "Leer el Aviso de Privacidad" },
  },
  {
    question: "¿Puedo cancelar cuando quiera?",
    answer:
      "Sí. Puedes cancelar escribiéndole a Koach en el chat. Las condiciones para conservar tu precio Founder estarán en los Términos y Condiciones.",
  },
  {
    question: "¿Quién puede usar Koach?",
    answer:
      "Personas mayores de 18 años. Koach no está pensado para menores de edad.",
  },
];

export const LEGAL_LINKS = [
  { href: "/privacidad", label: "Aviso de Privacidad" },
  { href: "/terminos", label: "Términos y Condiciones" },
  { href: "/disclaimer-medico", label: "Aviso médico" },
] as const;
