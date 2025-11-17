# chatbot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .mongo import get_db
from .ollama import generar_respuesta_normal
from .crisis_detector import detectar_nivel_crisis
from .respuetas_empaticas import respuestas_nivel1, respuestas_nivel2
from .crisis_handler import is_crisis_message, get_crisis_response
from .utils import guardar_historial
from chatbot.contexto import obtener_contexto_concatenado
import random

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


@csrf_exempt
@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"reply": "No recibí ningún mensaje."})

            # Llamar a MOGI pasando session
            response_text = responder_mogi(user_message, request.session)

            # Guardar historial solo si no es crisis
            if not is_crisis_message(user_message):
                guardar_historial(user_message, response_text)

            return JsonResponse({"reply": response_text})

        except Exception as e:
            return JsonResponse({"reply": f"Ocurrió un error: {str(e)}"})

    return JsonResponse({"reply": "Envía un mensaje usando POST."})