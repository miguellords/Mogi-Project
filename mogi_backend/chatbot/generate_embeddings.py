# generate_embeddings.py
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# 1️⃣ Conectar a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mogi_db"]

# 2️⃣ Cargar modelo de embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# 3️⃣ Cargar todas las frases de responses_dataset
responses = list(db.responses_dataset.find({}))

# 4️⃣ Generar embeddings si no existen y guardarlos
for r in responses:
    if not r.get("embedding"):  # Si el embedding está vacío
        embedding = model.encode(r["frase"]).tolist()
        # Actualizar la frase con su embedding
        db.responses_dataset.update_one(
            {"_id": r["_id"]},
            {"$set": {"embedding": embedding}}
        )
        # Guardar en la cache de embeddings
        db.embeddings_cache.insert_one({
            "text": r["frase"],
            "embedding": embedding
        })

print("✅ Embeddings generados para todas las frases existentes en MongoDB")
