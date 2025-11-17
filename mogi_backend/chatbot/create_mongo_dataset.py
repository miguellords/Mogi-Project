from pymongo import MongoClient
import json
from pathlib import Path

# --- CONFIGURAR ---
DATASET_PATH = Path("mogi_dataset_5000.jsonl")
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "mogi_db"
COLLECTION_NAME = "responses_dataset"


def main():
    # Conectar a MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[COLLECTION_NAME]

    print("⚠ Eliminando colección anterior (si existe)...")
    col.drop()

    print("📥 Leyendo dataset...")
    items = []
    with DATASET_PATH.open(encoding="utf-8") as f:
        for line in f:
            items.append(json.loads(line))

    print(f"📦 Insertando {len(items)} documentos en MongoDB...")
    col.insert_many(items)

    print("✅ COMPLETADO: Dataset cargado en MongoDB correctamente.")


if __name__ == "__main__":
    main()
