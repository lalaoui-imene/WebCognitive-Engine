from pathlib import Path
import chromadb

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Dossier de stockage de la base vectorielle
DB_DIR = BASE_DIR / "chroma_db"

# Initialisation de la base locale persistante
client = chromadb.PersistentClient(
    path=str(DB_DIR)
)

# Création ou récupération de la collection
collection = client.get_or_create_collection(
    name="webcognitive_documents",
    metadata={"hnsw:space": "cosine"}
)

print("Base vectorielle initialisée avec succès !")
print(f"Emplacement : {DB_DIR}")
print(f"Collection : {collection.name}")
print(f"Nombre de vecteurs : {collection.count()}")