# chatbot/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message", "")
        # Aquí integras la lógica de tu chatbot
        return JsonResponse({"reply": f"Recibí tu mensaje: {message}"})
    return JsonResponse({"error": "Método no permitido"}, status=405)

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
