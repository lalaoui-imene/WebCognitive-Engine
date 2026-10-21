
from pathlib import Path
import json

from pydantic import BaseModel, Field
import chromadb
from fastapi import FastAPI, HTTPException


# ============================================================
# INITIALISATION DE L'API
# ============================================================

app = FastAPI(
    title="WebCognitive Engine",
    description=(
        "API REST d'indexation et d'interrogation "
        "du corpus documentaire avec traçabilité des pages"
    ),
    version="1.1.0"
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_CLEAN_DIR = BASE_DIR / "data_clean"
DATA_VECTORS_DIR = BASE_DIR / "data_vectors_pages"
DB_DIR = BASE_DIR / "chroma_db"

NOM_MODELE = "all-MiniLM-L6-v2"
NOM_COLLECTION = "webcognitive_documents_pages"

TAILLE_LOT = 100


# ============================================================
# CONNEXION À CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=str(DB_DIR)
)

collection = client.get_or_create_collection(
    name=NOM_COLLECTION,
    metadata={"hnsw:space": "cosine"}
)


# ============================================================
# ROUTE D'ACCUEIL
# ============================================================

@app.get("/")
def accueil():

    return {
        "message": "Bienvenue sur WebCognitive Engine",
        "statut": "API opérationnelle",
        "collection": NOM_COLLECTION,
        "documents_nettoyes": len(
            list(DATA_CLEAN_DIR.glob("*.json"))
        ),
        "documents_vectorises": len(
            list(DATA_VECTORS_DIR.glob("*.json"))
        ),
        "vecteurs_indexes": collection.count()
    }


# ============================================================
# ROUTE D'INDEXATION
# ============================================================

@app.post("/index")
def indexer_documents():

    # On utilise les chunks déjà vectorisés avec leurs pages.
    # On ne redécoupe pas les PDF.

    fichiers_json = sorted(
        DATA_VECTORS_DIR.glob("*.json")
    )

    if not fichiers_json:

        raise HTTPException(
            status_code=404,
            detail=(
                "Aucun document vectorisé trouvé "
                "dans data_vectors_pages."
            )
        )

    documents_traites = 0
    chunks_traites = 0
    chunks_ajoutes = 0
    chunks_existants = 0
    erreurs = []

    for fichier_json in fichiers_json:

        try:

            # ------------------------------------------------
            # 1. LECTURE DU DOCUMENT VECTORISÉ
            # ------------------------------------------------

            with open(
                fichier_json,
                "r",
                encoding="utf-8"
            ) as fichier:

                donnees = json.load(fichier)

            chunks = donnees["chunks"]

            if not chunks:

                raise ValueError(
                    "Aucun chunk dans le fichier."
                )

            # ------------------------------------------------
            # 2. PRÉPARATION DES DONNÉES
            # ------------------------------------------------

            ids = []
            textes = []
            embeddings = []
            metadonnees = []

            for chunk in chunks:

                chunk_id = chunk["chunk_id"]

                identifiant = (
                    f"{fichier_json.stem}_{chunk_id}"
                )

                metadata = {
                    "source": donnees["source"],
                    "format": donnees["format"],
                    "chunk_id": chunk_id,
                    "date": donnees.get("date") or "",
                    "modele": donnees.get(
                        "modele_embedding",
                        NOM_MODELE
                    )
                }

                # Ajouter la page uniquement si disponible
                numero_page = chunk.get(
                    "numero_page"
                )

                if numero_page is not None:

                    metadata["numero_page"] = int(
                        numero_page
                    )

                ids.append(identifiant)
                textes.append(chunk["texte"])
                embeddings.append(chunk["embedding"])
                metadonnees.append(metadata)

            # ------------------------------------------------
            # 3. VÉRIFICATION DES CHUNKS EXISTANTS
            # ------------------------------------------------

            indices_manquants = []

            for debut in range(
                0,
                len(ids),
                TAILLE_LOT
            ):

                fin = debut + TAILLE_LOT

                resultat = collection.get(
                    ids=ids[debut:fin],
                    include=[]
                )

                ids_existants = set(
                    resultat["ids"]
                )

                for index in range(
                    debut,
                    min(fin, len(ids))
                ):

                    if ids[index] not in ids_existants:

                        indices_manquants.append(
                            index
                        )

            # ------------------------------------------------
            # 4. INDEXATION DES CHUNKS MANQUANTS
            # ------------------------------------------------

            for debut in range(
                0,
                len(indices_manquants),
                TAILLE_LOT
            ):

                indices = indices_manquants[
                    debut:debut + TAILLE_LOT
                ]

                collection.upsert(
                    ids=[
                        ids[index]
                        for index in indices
                    ],
                    documents=[
                        textes[index]
                        for index in indices
                    ],
                    embeddings=[
                        embeddings[index]
                        for index in indices
                    ],
                    metadatas=[
                        metadonnees[index]
                        for index in indices
                    ]
                )

            # ------------------------------------------------
            # 5. COMPTEURS
            # ------------------------------------------------

            documents_traites += 1
            chunks_traites += len(chunks)

            chunks_ajoutes += len(
                indices_manquants
            )

            chunks_existants += (
                len(chunks) - len(indices_manquants)
            )

        except Exception as erreur:

            erreurs.append({
                "fichier": fichier_json.name,
                "erreur": str(erreur)
            })

    # --------------------------------------------------------
    # 6. BILAN JSON
    # --------------------------------------------------------

    return {
        "statut": (
            "terminé"
            if not erreurs
            else "partiel"
        ),
        "collection": NOM_COLLECTION,
        "documents_traites": documents_traites,
        "chunks_traites": chunks_traites,
        "chunks_ajoutes": chunks_ajoutes,
        "chunks_existants": chunks_existants,
        "nombre_erreurs": len(erreurs),
        "vecteurs_en_base": collection.count(),
        "modele_embedding": NOM_MODELE,
        "erreurs": erreurs
    }


# ============================================================
# ROUTE D'INTERROGATION DU RAG
# ============================================================

class QuestionRAG(BaseModel):

    question: str = Field(
        min_length=1
    )


@app.post("/ask")
def poser_question(donnees: QuestionRAG):

    try:

        from rag import (
            rechercher_passages,
            generer_reponse
        )

        # ----------------------------------------------------
        # 1. RECHERCHE DES PASSAGES
        # ----------------------------------------------------

        passages = rechercher_passages(
            donnees.question
        )

        if not passages:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Aucun passage pertinent trouvé."
                )
            )

        # ----------------------------------------------------
        # 2. GÉNÉRATION AVEC OLLAMA
        # ----------------------------------------------------

        reponse = generer_reponse(
            donnees.question,
            passages
        )

        # ----------------------------------------------------
        # 3. CONSTRUCTION DES SOURCES
        # ----------------------------------------------------

        sources = []

        for passage in passages:

            numero_page = passage.get(
                "numero_page"
            )

            source = {
                "numero": passage["numero"],
                "document": passage["source"],
                "numero_page": numero_page,
                "chunk_id": passage["chunk_id"],
                "score_reranking": passage[
                    "score_reranking"
                ],
                "extrait": passage["texte"][:500]
            }

            sources.append(source)

        # ----------------------------------------------------
        # 4. RÉPONSE JSON
        # ----------------------------------------------------

        return {
            "question": donnees.question,
            "reponse": reponse,
            "nombre_sources": len(sources),
            "sources": sources
        }

    except HTTPException:

        raise

    except Exception as erreur:

        raise HTTPException(
            status_code=500,
            detail=str(erreur)
        )
