
from pathlib import Path
import chromadb

BASE_DIR = Path(__file__).resolve().parent.parent

client = chromadb.PersistentClient(
    path=str(BASE_DIR / "chroma_db")
)

collection = client.get_collection(
    name="webcognitive_documents"
)

# Vérifier que le vecteur de test existe
resultat = collection.get(
    ids=["test_indexation_0"],
    include=[]
)

if resultat["ids"]:
    collection.delete(ids=["test_indexation_0"])
    print("Vecteur de test supprimé.")
else:
    print("Aucun vecteur de test trouvé.")

print("Vecteurs restants :", collection.count())
