# crisis_detector.py

import re
import subprocess

# =============================================================
# 1. DETECTOR POR REGLAS (RÁPIDO Y EXACTO)
# =============================================================

def detectar_nivel_crisis_regex(texto_usuario: str) -> int:
    """
    Niveles:
    0 = no crisis
    1 = dolor emocional fuerte (sin intención)
    2 = riesgo moderado (ideas pasivas de muerte)
    3 = emergencia real (intención + plan)
    """

    texto = texto_usuario.lower().strip()

    # 🔴 NIVEL 3 — EMERGENCIA REAL
    patrones_nivel3 = [
        r"me voy a matar",
        r"voy a matarme",
        r"quiero matarme",
        r"quiero suicidarme",
        r"tengo un plan",
        r"hacerme daño ahora",
        r"lo haré hoy",
        r"ya no quiero vivir y voy a hacerlo",
        r"ya tomé una decisión",
    ]
    for p in patrones_nivel3:
        if re.search(p, texto):
            return 3

    # 🟡 NIVEL 2 — RIESGO MODERADO
    patrones_nivel2 = [
        r"quisiera no existir",
        r"quisiera desaparecer",
        r"quisiera no despertarme",
        r"a veces pienso en morir",
        r"ojalá no despertara",
        r"me gustaría dejar de vivir",
        r"pensado en hacerme daño",
    ]
    for p in patrones_nivel2:
        if re.search(p, texto):
            return 2

    # 🟢 NIVEL 1 — DOLOR EMOCIONAL
    patrones_nivel1 = [
        r"me siento tan mal",
        r"no quiero seguir así",
        r"ya no puedo más",
        r"me siento vacío",
        r"me siento destrozado",
        r"estoy muy triste",
        r"no tengo fuerzas",
        r"quiero rendirme",
        r"quisiera morir",  # sin plan
    ]
    for p in patrones_nivel1:
        if re.search(p, texto):
            return 1

    return 0


# =============================================================
# 2. CLASIFICACIÓN CON OLLAMA (INTELIGENCIA SEMÁNTICA)
# =============================================================

def clasificar_crisis_ollama(texto_usuario: str) -> int:
    """
    Usa LLaMA en Ollama para clasificar el nivel de crisis.
    Devuelve solo un número (0-3).
    """
    prompt = f"""
Clasifica el siguiente mensaje en uno de estos niveles:
0 = no crisis
1 = dolor emocional fuerte
2 = riesgo moderado (ideas pasivas de muerte)
3 = emergencia real (intención + plan)

Responde SOLO un número, sin explicación.

Mensaje:
"{texto_usuario}"
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.1"],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )

        salida = result.stdout.decode().strip()

        # A veces el modelo devuelve texto tipo "Nivel: 2" → extraemos número
        match = re.search(r"\b[0-3]\b", salida)
        if match:
            return int(match.group())

    except Exception:
        return 0  # fallback seguro si algo falla

    return 0


# =============================================================
# 3. DETECTOR FINAL (HÍBRIDO: REGEX + IA SEMÁNTICA)
# =============================================================

def detectar_nivel_crisis(texto_usuario: str) -> int:
    """
    Regresa el nivel más alto entre regex y Ollama.
    Más seguro y más preciso.
    """

    nivel_regex = detectar_nivel_crisis_regex(texto_usuario)

    # Si hay emergencia real → no preguntamos a IA
    if nivel_regex == 3:
        return 3

    # Para todo lo demás → IA analiza contextualmente
    nivel_ia = clasificar_crisis_ollama(texto_usuario)

    # Tomamos siempre el nivel más alto
    return max(nivel_regex, nivel_ia)
