# mongo.py
from pymongo import MongoClient
from datetime import datetime
from .crisis_handler import is_crisis_message

# ----------------------------------------------------------
# Conexión a la base de datos
# ----------------------------------------------------------
def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    return client["mogi_db"]  # Nombre de la base de datos


db = get_db()

