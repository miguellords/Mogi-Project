from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .mongo import get_db

db = get_db()

# ------------------------------------------
# 1. Guardar historial en Mongo
# ------------------------------------------
def guardar_historial(user_id, user_message, bot_message, display_name=None):
    """
    Guarda un mensaje del usuario y la respuesta del bot en MongoDB.
    """
    try:
        db.chat_history.insert_one({
            "user_id": user_id,
            "display_name": display_name,
            "message_user": user_message,
            "message_bot": bot_message,
            "timestamp": datetime.utcnow()
        })
    except Exception as e:
        print(f"⚠ Error guardando historial: {e}")

# ------------------------------------------
# 2. Obtener contexto por usuario
# ------------------------------------------
def obtener_contexto_usuario(user_id, n=5):
    """
    Devuelve los últimos n mensajes de un usuario específico.
    """
    historial = list(
        db.chat_history.find({"user_id": user_id}).sort("timestamp", -1).limit(n)
    )
    historial.reverse()
    contexto = ""
    for h in historial:
        contexto += f"Usuario: {h['message_user']}\nMOGI: {h['message_bot']}\n"
    return contexto
# ------------------------------------------
# 3. Búsqueda semántica
# ------------------------------------------
def find_most_similar(user_embedding):
    responses = list(db.responses_dataset.find({}))
    embeddings = np.array([r["embedding"] for r in responses])
    # Aquí iría la lógica de cosine_similarity
