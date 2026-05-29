# Todos los mensajes que Koach envía al usuario.
# Nunca escribir strings de mensajes fuera de este archivo.

BIENVENIDA_Y_CONSENTIMIENTO = (
    "¡Hola! 👋 Soy *Koach*, tu coach de salud personal por WhatsApp.\n\n"
    "Te ayudaré a mejorar tu alimentación y hábitos de forma personalizada, directo desde aquí.\n\n"
    "Antes de empezar, necesito guardar algunos datos básicos tuyos para crear tu plan. "
    "¿Me das tu consentimiento?\n\n"
    "Responde *sí* para continuar o *no* si prefieres no hacerlo.\n"
    "(Consulta nuestro aviso de privacidad en koach.mx/privacidad)"
)

CONSENTIMIENTO_RECHAZADO = (
    "Entendido, no hay problema. 🙏\n\n"
    "Si en algún momento cambias de opinión, escríbeme de nuevo y con gusto empezamos.\n\n"
    "Aviso de privacidad: koach.mx/privacidad"
)

PREGUNTAS: dict[int, str] = {
    1: "¡Perfecto! Empecemos. 😊 ¿Cómo te llamas?",
    2: "¿Cuántos años tienes? (Solo el número, por ejemplo: *28*)",
    3: "¿Cuánto pesas actualmente? (Solo el número en kg, por ejemplo: *75*)",
    4: "¿Cuánto mides? (Solo el número en cm, por ejemplo: *170*)",
    5: "¿Cuál es tu género?\nResponde: *hombre*, *mujer* o *prefiero no decir*",
    6: (
        "¿Cuál es tu meta principal? Responde una de estas:\n"
        "• *bajar de peso*\n"
        "• *ganar músculo*\n"
        "• *comer mejor*\n"
        "• *más energía*"
    ),
    7: (
        "Por último, ¿tienes alguna alergia o condición alimentaria que deba conocer? "
        "(Si no tienes ninguna, escribe *ninguna*)"
    ),
}

RESPUESTA_INVALIDA: dict[int, str] = {
    1: "Hmm, no entendí bien. ¿Puedes escribir solo tu nombre? (Ejemplo: *María*)",
    2: "Por favor escribe solo tu edad en números. (Ejemplo: *25*)",
    3: "Por favor escribe solo tu peso en kilos. (Ejemplo: *70*)",
    4: "Por favor escribe solo tu estatura en centímetros. (Ejemplo: *165*)",
    5: "Por favor responde *hombre*, *mujer* o *prefiero no decir*",
    6: (
        "Por favor elige una de estas opciones:\n"
        "• *bajar de peso*\n"
        "• *ganar músculo*\n"
        "• *comer mejor*\n"
        "• *más energía*"
    ),
    7: "Por favor escríbeme tus alergias o condiciones. Si no tienes, escribe *ninguna*",
}

DEMASIADOS_INTENTOS = (
    "Parece que tenemos un problema de comunicación. 😅 "
    "Escribe *reiniciar* para comenzar de nuevo."
)

ERROR_TECNICO = "Tuve un pequeño problema técnico. 🔧 Intenta de nuevo en unos minutos."

ERROR_EDAD_MINIMA = (
    "Gracias por tu interés 💙, pero Koach está disponible solo para personas de 13 años o más. "
    "¡Cuídate mucho!"
)


def confirmacion_peso(peso: float) -> str:
    return f"¿Estás seguro de que pesas *{peso} kg*? Responde *sí* para confirmar o *no* para corregir."


def onboarding_completo(nombre: str) -> str:
    return (
        f"¡Listo {nombre}! 🎉 Ya tengo todos tus datos. "
        "Estoy generando tu plan personalizado, te lo comparto en unos momentos."
    )


def hola_de_nuevo(nombre: str) -> str:
    return f"¡Hola de nuevo {nombre}! 👋"
