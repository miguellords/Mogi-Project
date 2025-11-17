from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .mongo import get_db

db = get_db()

# ------------------------------------------
# 1. Guardar historial en Mongo
# ------------------------------------------
def guardar_historial(user_message, bot_message):
    """
    Guarda un mensaje del usuario y la respuesta del bot en MongoDB.
    """
    try:
        db.chat_history.insert_one({
            "message_user": user_message,
            "message_bot": bot_message,
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        print(f"⚠ Error guardando historial: {e}")


# ------------------------------------------
# 2. Obtener contexto (últimos mensajes)
# ------------------------------------------
def obtener_contexto(n=5):
    """
    Devuelve los últimos n mensajes del historial para usar como contexto.
    """
    historial = list(
        db.chat_history.find().sort("timestamp", -1).limit(n)
    )
    
    historial = reversed(historial)  # para que queden en orden cronológico
    
    contexto = ""
    for h in historial:
        contexto += f"Usuario: {h['message_user']}\n"
        contexto += f"MOGI: {h['message_bot']}\n"
    return contexto


# ------------------------------------------
# 3. Búsqueda semántica
# ------------------------------------------
def find_most_similar(user_embedding):
    """
    Busca la respuesta más similar mediante embeddings.
    """
    responses = list(db.responses_dataset.find({}))
    embeddings = np.array([r["embedding"] for r in responses])
