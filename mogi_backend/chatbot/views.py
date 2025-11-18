# chatbot/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from datetime import datetime
import random

from .mongo import get_db
from .ollama import generar_respuesta_normal
from .crisis_detector import detectar_nivel_crisis
from .respuetas_empaticas import respuestas_nivel1, respuestas_nivel2
from .crisis_handler import is_crisis_message, get_crisis_response

# -----------------------------
# Funciones utilitarias
# -----------------------------
def guardar_historial(user_id, mensaje_usuario, mensaje_bot, display_name=""):
    # Siempre guardamos en Mongo, pero solo para historial, no para contexto
    from .mongo import get_db
    db = get_db()
    db.chat_history.insert_one({
        "user_id": user_id,
        "display_name": display_name,
        "message_user": mensaje_usuario,
        "message_bot": mensaje_bot,
        "timestamp": datetime.utcnow()
    })

# -----------------------------
# API principal del chatbot
# -----------------------------
@csrf_exempt
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Usa POST para enviar mensajes."})

    # Inicializar contexto de sesión si no existe
    if "contexto_actual" not in request.session:
        request.session['contexto_actual'] = ""

    try:
        data = json.loads(request.body)
        user_id = data.get("user_id", "anonimo")
        display_name = data.get("display_name", "")
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"reply": "No recibí ningún mensaje."})

        # -----------------------------
        # Detectar crisis
        # -----------------------------
        if is_crisis_message(user_message):
            respuesta = get_crisis_response(user_message)
            guardar_historial(user_id, user_message, respuesta, display_name)
            return JsonResponse({"reply": respuesta})

        nivel = detectar_nivel_crisis(user_message)
        if nivel == 2:
            respuesta = random.choice(respuestas_nivel2)
            guardar_historial(user_id, user_message, respuesta, display_name)
            return JsonResponse({"reply": respuesta})
        elif nivel == 1:
            respuesta = random.choice(respuestas_nivel1)
            guardar_historial(user_id, user_message, respuesta, display_name)
            return JsonResponse({"reply": respuesta})

        # -----------------------------
        # Cambio de tema
        # -----------------------------
        if user_message.lower() in ["nuevo tema", "reset contexto", "cambiar conversación"]:
            request.session['contexto_actual'] = ""  # reinicia contexto
            respuesta = "Perfecto, comenzamos un nuevo tema. Puedes contarme lo que quieras desde ahora."
            guardar_historial(user_id, user_message, respuesta, display_name)
            return JsonResponse({"reply": respuesta})

        # -----------------------------
        # Flujo normal usando contexto de sesión
        # -----------------------------
        contexto = request.session.get('contexto_actual', "")
        prompt = f"{contexto}Usuario: {user_message}\nMOGI:"

        respuesta = generar_respuesta_normal(prompt, user_id)

        # Actualizar contexto en sesión solo con este intercambio
        request.session['contexto_actual'] += f"Usuario: {user_message}\nMOGI: {respuesta}\n"

        # Guardar historial completo
        guardar_historial(user_id, user_message, respuesta, display_name)

        return JsonResponse({"reply": respuesta})

    except Exception as e:
        return JsonResponse({"reply": f"Ocurrió un error: {str(e)}"})


# -----------------------------
# Autenticación con Google
# -----------------------------
@api_view(["POST"])
def google_auth(request):
    access_token = request.data.get("access_token")
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    from .models import Usuario
    user, _ = Usuario.objects.get_or_create(
        email=user_info["email"],
        defaults={"nombre": user_info["name"]}
    )

    return Response({"status": "ok", "user": user_info})
