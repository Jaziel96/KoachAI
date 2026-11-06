import { PENDING, type LegalDocument } from "./types";

/**
 * Borrador del Aviso de Privacidad (US-014). Fuentes: plan-maestro §19.2 y
 * analisis-brechas §1.3. El texto final lo redacta un abogado (P-04, P-05).
 */
export const privacidad: LegalDocument = {
  slug: "privacidad",
  title: "Aviso de Privacidad",
  description:
    "Cómo Koach recaba, usa y protege tus datos personales, y cómo ejercer tus derechos ARCO.",
  version: "0.1 (borrador)",
  updatedAt: "2026-11-06",
  sections: [
    {
      id: "responsable",
      title: "Responsable de tus datos",
      paragraphs: [
        `El responsable de tus datos personales es ${PENDING.responsable}.`,
        `Para cualquier asunto sobre tus datos puedes escribir a ${PENDING.email}.`,
      ],
    },
    {
      id: "datos",
      title: "Datos que recabamos",
      paragraphs: [
        "Para acompañarte recabamos los datos que tú nos compartes en la conversación de WhatsApp:",
      ],
      items: [
        "Datos de contacto, como tu número de WhatsApp.",
        "Datos personales de perfil, como edad, estatura y peso.",
        "Datos sensibles de salud y hábitos, como tus metas, tu alimentación y tus respuestas a cuestionarios de salud.",
        "Los mensajes que intercambias con Koach.",
        "Si te registras en la lista de espera: tu correo, tu nombre y tu meta principal.",
      ],
    },
    {
      id: "finalidad",
      title: "Para qué usamos tus datos",
      items: [
        "Darte orientación alimentaria y acompañamiento de hábitos.",
        "Personalizar las sugerencias con base en tu meta y tu alacena.",
        "Enviarte recordatorios y mensajes de seguimiento.",
        "Avisarte cuando Koach esté disponible, si te registraste en la lista de espera.",
        "Mejorar la seguridad y el funcionamiento del servicio.",
      ],
    },
    {
      id: "consentimiento",
      title: "Consentimiento para datos de salud",
      paragraphs: [
        "Los datos de salud son datos sensibles. Antes de pedírtelos, Koach te solicitará tu consentimiento expreso dentro de la conversación, y guardaremos constancia de la fecha y de la versión de este aviso que aceptaste.",
      ],
    },
    {
      id: "terceros",
      title: "Con quién compartimos tus datos",
      paragraphs: [
        "Para operar el servicio usamos proveedores tecnológicos que procesan información por cuenta nuestra:",
      ],
      items: [
        "Anthropic y otros proveedores de inteligencia artificial, para generar las respuestas de Koach.",
        "Meta (WhatsApp), para enviar y recibir mensajes.",
        "Supabase, para almacenar tu información.",
        "Google, cuando se utilice para funciones del servicio.",
      ],
    },
    {
      id: "transferencia",
      title: "Transferencia internacional de datos",
      paragraphs: [
        "Estos proveedores tienen servidores en Estados Unidos, por lo que tus datos pueden transferirse y almacenarse fuera de México. Al usar Koach y aceptar este aviso, consientes esa transferencia. Procuramos enviar a los proveedores de inteligencia artificial solo la información necesaria, sin tu nombre completo, teléfono ni correo.",
      ],
    },
    {
      id: "arco",
      title: "Tus derechos ARCO",
      paragraphs: [
        "Tienes derecho a Acceder, Rectificar, Cancelar u Oponerte al uso de tus datos. Puedes ejercerlos escribiendo estos comandos en tu chat con Koach:",
      ],
      items: [
        "MIS DATOS: te muestra un resumen de lo que tenemos de ti.",
        "RECTIFICAR [dato]: corrige un dato.",
        "EXPORTAR MIS DATOS: recibes una copia de tu información.",
        "BORRAR MIS DATOS: cancelamos tu cuenta y eliminamos tus datos.",
      ],
    },
    {
      id: "plazos",
      title: "Plazo de respuesta",
      paragraphs: [
        "Atenderemos tu solicitud en un máximo de 20 días hábiles.",
      ],
    },
    {
      id: "conservacion",
      title: "Cuánto tiempo conservamos tus datos",
      paragraphs: [
        "Conservamos tus datos mientras tu cuenta esté activa y durante el tiempo que la ley nos exija.",
      ],
    },
    {
      id: "cambios",
      title: "Cambios a este aviso",
      paragraphs: [
        "Si modificamos este aviso te lo notificaremos por WhatsApp y publicaremos la nueva versión en esta página, con su fecha de actualización.",
      ],
    },
  ],
};
