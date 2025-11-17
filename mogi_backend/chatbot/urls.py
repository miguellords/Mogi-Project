from django.urls import path
from .views import chatbot_api
from .views import google_auth

urlpatterns = [
    path('', chatbot_api, name='chatbot_api'),
]

path("api/auth/google/", google_auth),