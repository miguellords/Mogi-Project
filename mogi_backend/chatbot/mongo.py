# mongo.py
from pymongo import MongoClient
from datetime import datetime

# ----------------------------------------------------------
# Conexión a la base de datos
# ----------------------------------------------------------
def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    return client["mogi_db"]  # Nombre de la base de datos


db = get_db()


# ----------------------------------------------------------
# Guardar historial del chat
# ----------------------------------------------------------
def guardar_historial(user_msg, bot_msg):
    db.chat_history.insert_one({
        "message_user": user_msg,
        "message_bot": bot_msg,
        "timestamp": datetime.utcnow()
    })


# ----------------------------------------------------------
# Obtener contexto normal (si quieres seguir usándolo)
# ----------------------------------------------------------
def obtener_contexto(n=5):
    historial = list(db.chat_history.find().sort("timestamp", -1).limit(n))
    historial = reversed(historial)

    contexto = ""
    for h in historial:
        contexto += f"Usuario: {h['message_user']}\n"
        contexto += f"MOGI: {h['message_bot']}\n"

    return contexto


# ----------------------------------------------------------
# 🔥 Nuevo: contexto concatenado para memoria conversacional
# ----------------------------------------------------------
from .crisis_handler import is_crisis_message

def obtener_contexto_concatenado(n=5):
    historial = list(db.chat_history.find().sort("timestamp", -1).limit(n*2))  # tomamos más para filtrar
    historial = reversed(historial)

    contexto = ""
    count = 0
    for mensaje in historial:
        # Ignorar mensajes de crisis
        if is_crisis_message(mensaje["message_user"]):
            continue

        contexto += f"Usuario: {mensaje['message_user']}\nBot: {mensaje['message_bot']}\n"
        count += 1
        if count >= n:
            break

    return contexto
