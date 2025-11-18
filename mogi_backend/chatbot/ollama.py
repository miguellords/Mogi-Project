# chatbot/ollama.py
import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .generate_embeddings import model
from .utils import find_most_similar

def llama_generate_response(prompt: str):
    """
    Envía un prompt a Ollama y devuelve la respuesta del modelo MOGI.
    """
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "mogi",   # Modelo personalizado
            "prompt": prompt,
            "stream": False
        }

        res = requests.post(url, json=payload)
        res.raise_for_status()

        data = res.json()
        return data.get("response", "No pude generar una respuesta adecuada.")

    except Exception as e:
        return f"No pude generar respuesta con MOGI/LLaMA: {e}"


def generar_respuesta_normal(prompt, user_id=None):
    """
    Genera la respuesta de MOGI:
    1. Coincidencia literal
    2. Coincidencia semántica
    3. Respuesta generativa con MOGI
    """

    # --- 1. Coincidencia literal ---
    from .mongo import get_db
    db = get_db()
    literal = db.responses_dataset.find_one({"frase": prompt.lower()})
    if literal:
        return literal["respuesta"]

    # --- 2. Coincidencia semántica ---
    user_embedding = model.encode(prompt)
    best_match = find_most_similar(user_embedding)

    if best_match:
        similarity = cosine_similarity(
            user_embedding.reshape(1, -1),
            np.array(best_match["embedding"]).reshape(1, -1)
        )[0][0]

        if similarity > 0.65:
            return best_match["respuesta"]

    # --- 3. Generar respuesta con MOGI usando solo contexto de sesión ---
    # Ya recibimos el contexto concatenado desde views.py
    final_prompt = f"""
Eres MOGI, un asistente emocional cálido, empático, cercano y profundo.

INSTRUCCIONES:
- Responde con mucha empatía, calidez y contención emocional.
- Ofrece respuestas largas (mínimo 150–250 palabras).
- Sé reflexivo, humano, cercano y natural.
- No repitas lo que el usuario dice.
- No hagas preguntas repetitivas.
- Valida emociones sin patologizar ni sonar como terapeuta profesional.
- Habla como un amigo sabio que acompaña de verdad.
- Integra el contexto previo proporcionado de forma natural.

Contexto actual del usuario (solo de esta sesión):
{prompt}

MOGI (responde con profundidad emocional, calidez y un solo mensaje, extenso y humano):
"""
    return llama_generate_response(final_prompt).strip()
