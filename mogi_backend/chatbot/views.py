# chatbot/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .mongo import get_db
from .ollama import generar_respuesta_normal
from .crisis_detector import detectar_nivel_crisis
from .respuetas_empaticas import respuestas_nivel1, respuestas_nivel2
from .crisis_handler import is_crisis_message, get_crisis_response
from .utils import guardar_historial, obtener_contexto_usuario
from chatbot.contexto import obtener_contexto_concatenado
import random

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")            # UID de Supabase
            display_name = data.get("display_name", "")  # opcional
            user_message = data.get("message", "").strip()

            if not user_id:
                return JsonResponse({"reply": "Error: falta user_id."})
            if not user_message:
                return JsonResponse({"reply": "No recibí ningún mensaje."})

            # Obtener contexto y generar respuesta
            contexto = obtener_contexto_usuario(user_id, 5)
            prompt = contexto + f"\nUsuario: {user_message}\nMOGI:"
            respuesta = generar_respuesta_normal(prompt)

            # Guardar historial correctamente
            guardar_historial(user_id, user_message, respuesta, display_name)

            return JsonResponse({"reply": respuesta})

        except Exception as e:
            return JsonResponse({"reply": f"Ocurrió un error: {str(e)}"})

    return JsonResponse({"reply": "Usa POST para enviar mensajes."})



#REGISTRO DE AUTENTICACIÓN CON GOOGLE
@api_view(["POST"])
def google_auth(request):
    access_token = request.data.get("access_token")

    # Validar token con Google
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    # Crear/obtener usuario
    from .models import Usuario
    user, _ = Usuario.objects.get_or_create(
        email=user_info["email"],
        defaults={"nombre": user_info["name"]}
    )

    return Response({"status": "ok", "user": user_info})

# MongoDB
db = get_db()

def responder_mogi(texto_usuario: str, session):
    """
    Función completa de MOGI:
    - Detecta crisis graves y leves
    - Maneja cambio de tema con confirmación
    - Guarda y filtra el contexto usando session
    """
    texto_lower = texto_usuario.lower().strip()

    # 🚨 1. Crisis grave
    if is_crisis_message(texto_usuario):
        return get_crisis_response(texto_usuario)

    # 🟠 2. Crisis leve o moderada
    nivel = detectar_nivel_crisis(texto_usuario)
    if nivel == 2:
        return random.choice(respuestas_nivel2)
    if nivel == 1:
        return random.choice(respuestas_nivel1)

    # 🔄 3. Preguntar si se quiere cambiar el contexto
    if texto_lower in ["nuevo tema", "reset contexto", "cambiar conversación"]:
        session['confirmar_reset'] = True
        return "¿Quieres empezar un nuevo tema? Si es así, nuestra conversación actual no se tomará en cuenta para el contexto."

    # 🔄 4. Reiniciar contexto si el usuario confirma
    if texto_lower in ["sí", "si"] and session.get('confirmar_reset', False):
        session['contexto_actual'] = ""  # reinicia el contexto
        session['confirmar_reset'] = False
        return "Perfecto, comenzamos un nuevo tema. Puedes contarme lo que quieras desde ahora."

    # 🔄 5. Cancelar reset si el usuario dice no
    if texto_lower in ["no"] and session.get('confirmar_reset', False):
        session['confirmar_reset'] = False
        return "Está bien, seguimos con la conversación actual."

    # 🟢 6. Flujo normal con contexto
    contexto_guardado = session.get('contexto_actual', "")
    contexto = obtener_contexto_concatenado(5)  # obtiene últimos 5 intercambios

    # 🔹 Filtrar contexto antiguo de crisis
    if is_crisis_message(contexto_guardado):
        session['contexto_actual'] = ""
        contexto_guardado = ""

    # 🔹 Limpiar contexto si el usuario escribe algo normal y había crisis previas
    if not is_crisis_message(texto_usuario):
        if is_crisis_message(session.get("contexto_actual", "")):
            session['contexto_actual'] = ""
            contexto_guardado = ""

    # Concatenar contexto actualizado con el mensaje actual
    texto_para_modelo = contexto_guardado + contexto + "\nUsuario: " + texto_usuario
    respuesta = generar_respuesta_normal(texto_para_modelo)

    # Guardar contexto actualizado en session
    session['contexto_actual'] = texto_para_modelo

    return respuesta