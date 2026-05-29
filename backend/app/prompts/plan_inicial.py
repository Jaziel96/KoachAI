# app/prompts/plan_inicial.py

SYSTEM_PROMPT = """Eres Koach, un coach de salud personalizado para mexicanos. 
Tu tono es amigable, motivador y práctico.

REGLAS DE FORMATO — MUY IMPORTANTE:
- No uses Markdown: nada de ##, **, *, ni guiones como bullets
- Usa emojis como separadores visuales en lugar de símbolos
- Sé específico con porciones (ej: "1 taza de avena con leche descremada")
- Usa ingredientes fáciles de conseguir en México
- Todo en español mexicano, tono cálido y motivador"""


def construir_prompt(
    nombre: str,
    edad: int,
    peso_kg: float,
    talla_cm: int,
    genero: str,
    meta: str,
    alergias: str,
    tmb: float,
    tdee: float,
    meta_calorica: float,
) -> str:
    return f"""Genera el plan personalizado para este usuario:

Nombre: {nombre}
Edad: {edad} años | Peso: {peso_kg} kg | Talla: {talla_cm} cm | Género: {genero}
Meta principal: {meta}
Alergias o condiciones: {alergias}

Cálculos nutricionales:
TMB: {tmb:.0f} kcal/día
TDEE: {tdee:.0f} kcal/día
Meta calórica diaria: {meta_calorica:.0f} kcal/día

Usa EXACTAMENTE estos separadores para cada sección:

---RESUMEN---
[Explica en 2-3 oraciones qué significan TMB, TDEE y meta calórica 
para {nombre}, en lenguaje cotidiano sin términos técnicos]

---ALIMENTACION---
Desayuno ({round(meta_calorica * 0.25):.0f} kcal aprox.)
[3-4 opciones con cantidades específicas]

Comida ({round(meta_calorica * 0.35):.0f} kcal aprox.)
[3-4 opciones con cantidades específicas]

Cena ({round(meta_calorica * 0.25):.0f} kcal aprox.)
[2-3 opciones con cantidades específicas]

Snacks ({round(meta_calorica * 0.15):.0f} kcal aprox.)
[2-3 opciones con cantidades específicas]

---EJERCICIO---
[Plan de 3-4 días según la meta "{meta}".
Especifica tipo de ejercicio, duración y días sugeridos]

---CONSEJOS---
[Consejo 1 personalizado según alergias/condición]
[Consejo 2 personalizado según meta]
[Consejo 3 motivacional para el día 1]

CRÍTICO: NUNCA incluyas alimentos que contengan: {alergias}"""