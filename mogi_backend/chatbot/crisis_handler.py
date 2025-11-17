# chatbot/crisis_handler.py

import re

# 🔹 Palabras y frases que indican riesgo de suicidio o crisis grave
CRISIS_KEYWORDS = [
    r"\bquiero morir\b",
    r"\bno quiero vivir\b",
    r"\bme quiero matar\b",
    r"\bquitarme la vida\b",
    r"\bmatarme\b",
    r"\bhacerme daño\b",
    r"\blastimarme\b",
    r"\bya no puedo más\b",
    r"\bno veo salida\b",
    r"\bodio mi vida\b"
]

def is_crisis_message(message: str) -> bool:
    message_lower = message.lower()

    for pattern in CRISIS_KEYWORDS:
        if re.search(pattern, message_lower):
            return True

    return False

def get_crisis_response(message: str) -> str:
    """
    Genera una respuesta segura, empática y basada en protocolos de crisis.
    Incluye líneas de ayuda y recomendaciones generales.
    """
    response = (
        "Lamento mucho que estés pasando por un momento tan difícil. "
        "Quiero que sepas que no estás solo y que tu vida es valiosa.\n\n"
        "Si sientes que podrías hacerte daño a ti mismo, "
        "por favor contacta inmediatamente a alguien de confianza o a profesionales de ayuda:\n\n"
        "🇨🇴 **Líneas de ayuda en Colombia:**\n"
        "• (604) 540 71 80: Línea Salud para el  alma (Medellín)\n"
        "• (604) 444 44 48: Línea Amiga Saludable (Medellín, disponible las 24 horas)\n"
        "• Línea 123: Emergencias generales\n"
        "• 01 8000 112 137: Línea Púrpura\n"
        "• WhatsApp: 333 0333588, para recibir apoyo psicológico gratuito\n"
        "Te recomiendo buscar un lugar seguro y hablar con alguien que pueda escucharte. "
        "Estoy aquí contigo para escucharte y apoyarte.\n\n"
        "Puedes contarme más sobre cómo te sientes si quieres."
    )
    return response
