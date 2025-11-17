from chatbot.mongo import get_db

db = get_db()

def obtener_contexto(n=5):
    historial = list(db.chat_history.find().sort("timestamp", -1).limit(n))
    historial = reversed(historial)
    
    contexto = ""
    for h in historial:
        contexto += f"Usuario: {h['message_user']}\n"
        contexto += f"MOGI: {h['message_bot']}\n"
    
    return contexto


# ✅ NUEVA FUNCIÓN AQUÍ
def obtener_contexto_concatenado(n=5):
    historial = list(db.chat_history.find().sort("timestamp", -1).limit(n))
    historial = reversed(historial)

    partes = []
    for h in historial:
        partes.append(f"Usuario: {h['message_user']}")
        partes.append(f"MOGI: {h['message_bot']}")

    return "\n".join(partes)