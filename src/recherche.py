
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "chroma_db"

NOM_MODELE = "all-MiniLM-L6-v2"
TOP_K = 5
TOP_K_CANDIDATS = 30


# ============================================================
# CONNEXION À CHROMADB
# ============================================================

client = chromadb.PersistentClient(path=str(DB_DIR))

collection = client.get_collection(
    name="webcognitive_documents"
)

modele = SentenceTransformer(NOM_MODELE)


# ============================================================
# REFORMULATION DES QUESTIONS POUR LA RECHERCHE
# ============================================================

def preparer_requete(question):

    question_min = question.lower()

    if any(mot in question_min for mot in [
        "qu'est-ce", "qu’est-ce", "définition",
        "définir", "c'est quoi"
    ]):
        return (
            "What is a medical digital twin? "
            "Definition and explanation of digital twins "
            "in healthcare and personalized medicine."
        )

    if any(mot in question_min for mot in [
        "limite", "risque", "obstacle", "défi"
    ]):
        return (
            "Limitations, challenges, barriers and risks "
            "of digital twins in healthcare."
        )

    if "cardiolog" in question_min:
        return (
            "Applications of digital twins in cardiology "
            "and cardiovascular medicine."
        )

    if any(mot in question_min for mot in [
        "personnalis", "traitement"
    ]):
        return (
            "Applications and benefits of digital twins "
            "for personalized medicine and patient treatment."
        )

    return question


# ============================================================
# RECHERCHE SÉMANTIQUE
# ============================================================

def rechercher_passages(question, top_k=TOP_K):

    requete = preparer_requete(question)

    vecteur = modele.encode(requete).tolist()

    resultats = collection.query(
        query_embeddings=[vecteur],
        n_results=TOP_K_CANDIDATS,
        include=["documents", "metadatas", "distances"]
    )

    passages = []

    for i, texte in enumerate(resultats["documents"][0]):

        distance = resultats["distances"][0][i]
        metadata = resultats["metadatas"][0][i] or {}

        # Écarter certains passages peu exploitables
        if len(texte.strip()) < 100:
            continue

        passages.append({
            "texte": texte,
            "source": metadata.get("source", "Inconnue"),
            "chunk_id": metadata.get("chunk_id", i),
            "distance": distance,
            "similarite": round(1 - distance, 4)
        })

    passages.sort(
        key=lambda p: p["distance"]
    )

    passages = passages[:top_k]

    for i, passage in enumerate(passages):
        passage["numero"] = i + 1

    return passages


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    question = input("\nPose ta question : ")

    print("\nRequête utilisée :", preparer_requete(question))

    passages = rechercher_passages(question)

    for passage in passages:

        print(f"\n[Source {passage['numero']}]")
        print("Document :", passage["source"])
        print("Chunk :", passage["chunk_id"])
        print("Similarité :", passage["similarite"])
        print("Extrait :", passage["texte"][:500])
