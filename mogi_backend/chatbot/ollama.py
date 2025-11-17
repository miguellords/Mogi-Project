import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .mongo import get_db
from .generate_embeddings import model
from .contexto import obtener_contexto
from .utils import find_most_similar

db = get_db()


def llama_generate_response(prompt: str):
    """
    Envía un prompt a Ollama y devuelve la respuesta del modelo MOGI.
    """
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "mogi",   # Modelo personalizado definido en tu Modelfile
            "prompt": prompt,
            "stream": False
        }

        res = requests.post(url, json=payload)
        res.raise_for_status()

        data = res.json()
        return data.get("response", "No pude generar una respuesta adecuada.")

    except Exception as e:
        return f"No pude generar respuesta con MOGI/LLaMA: {e}"


def generar_respuesta_normal(texto_usuario):
    """
    Flujo normal del chatbot:
    1. Coincidencia literal
    2. Coincidencia semántica
    3. Respuesta generativa con MOGI
    """

    # --- 1. COINCIDENCIA LITERAL ---
    literal = db.responses_dataset.find_one({"frase": texto_usuario.lower()})
    if literal:
        return literal["respuesta"]

    # --- 2. COINCIDENCIA SEMÁNTICA ---
    user_embedding = model.encode(texto_usuario)
    best_match = find_most_similar(user_embedding)

    if best_match:
        similarity = cosine_similarity(
            user_embedding.reshape(1, -1),
            np.array(best_match["embedding"]).reshape(1, -1)
        )[0][0]

        if similarity > 0.65:
            return best_match["respuesta"]

    # --- 3. GENERAR RESPUESTA CON MOGI ---
    contexto = obtener_contexto(n=5) or "No hay mensajes previos."

    prompt = f"""
Eres MOGI, un asistente emocional cálido, empático, cercano y profundo.

INSTRUCCIONES IMPORTANTES:
- Responde con mucha empatía, calidez y contención emocional.
- Ofrece respuestas largas (mínimo 150–250 palabras).
- Sé reflexivo, humano, cercano y natural.
- No repitas lo que el usuario dice.
- No hagas preguntas repetitivas como “¿quieres contarme más?”.
- Valida emociones sin patologizar ni sonar como terapeuta profesional.
- Habla como un amigo sabio que acompaña de verdad.
- Integra el contexto previo de forma natural.

Contexto previo reciente de la conversación:
{contexto}

El usuario dice: "{texto_usuario}"

MOGI (responde con profundidad emocional, calidez y un solo mensaje, extenso y humano):
"""

    return llama_generate_response(prompt).strip()
