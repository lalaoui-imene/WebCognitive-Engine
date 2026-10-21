
from pathlib import Path
import json
import chromadb

# ============================================================
# CHEMINS ET CONNEXION À CHROMADB
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_VECTORS_DIR = BASE_DIR / "data_vectors_pages"
DB_DIR = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(DB_DIR))

# Nouvelle collection pour conserver l'ancienne intacte
NOM_COLLECTION = "webcognitive_documents_pages"

# Ne pas supprimer une collection existante
collection = client.get_or_create_collection(
    name=NOM_COLLECTION,
    metadata={"hnsw:space": "cosine"}
)

# ============================================================
# LECTURE DES DOCUMENTS VECTORISÉS
# ============================================================

fichiers_json = sorted(DATA_VECTORS_DIR.glob("*.json"))

print(f"Documents trouvés : {len(fichiers_json)}")

total_chunks = 0
nombre_erreurs = 0

# ============================================================
# INDEXATION DANS CHROMADB
# ============================================================

for fichier_json in fichiers_json:

    try:
        with open(
            fichier_json,
            "r",
            encoding="utf-8"
        ) as f:
            donnees = json.load(f)

        ids = []
        textes = []
        embeddings = []
        metadonnees = []

        for chunk in donnees["chunks"]:

            identifiant = (
                f"{fichier_json.stem}_{chunk['chunk_id']}"
            )

            ids.append(identifiant)
            textes.append(chunk["texte"])
            embeddings.append(chunk["embedding"])

            metadata = {
                "source": donnees["source"],
                "format": donnees["format"],
                "chunk_id": chunk["chunk_id"],
                "date": donnees.get("date") or "",
                "modele": donnees["modele_embedding"]
            }

            # Ajouter le numéro de page uniquement s'il existe
            # ChromaDB n'accepte pas les métadonnées None
            if chunk.get("numero_page") is not None:
                metadata["numero_page"] = int(
                    chunk["numero_page"]
                )

            metadonnees.append(metadata)

        # Insertion par lots
        TAILLE_LOT = 100

        for debut in range(0, len(ids), TAILLE_LOT):

            fin = debut + TAILLE_LOT

            collection.upsert(
                ids=ids[debut:fin],
                documents=textes[debut:fin],
                embeddings=embeddings[debut:fin],
                metadatas=metadonnees[debut:fin]
            )

        total_chunks += len(ids)

        print(
            f"[OK] {fichier_json.name} : "
            f"{len(ids)} chunks indexés"
        )

    except Exception as erreur:

        nombre_erreurs += 1

        print(
            f"[ERREUR] {fichier_json.name} : {erreur}"
        )

# ============================================================
# BILAN FINAL
# ============================================================

print("\n--- BILAN INDEXATION ---")

print(f"Documents trouvés : {len(fichiers_json)}")
print(f"Chunks traités : {total_chunks}")
print(f"Erreurs : {nombre_erreurs}")
print(
    f"Vecteurs présents dans ChromaDB : "
    f"{collection.count()}"
)

# ============================================================
# VÉRIFICATION DES NUMÉROS DE PAGE
# ============================================================

resultat = collection.get(
    where={"numero_page": {"$gte": 1}},
    limit=3,
    include=["metadatas"]
)

print("\n--- TEST MÉTADONNÉES ---")

for metadata in resultat["metadatas"]:

    print(
        f"Document : {metadata['source']} | "
        f"Page : {metadata['numero_page']} | "
        f"Chunk : {metadata['chunk_id']}"
    )
