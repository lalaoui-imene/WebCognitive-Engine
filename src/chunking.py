
from pathlib import Path
import json

from sentence_transformers import SentenceTransformer


# ============================================================
# CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_CLEAN_DIR = BASE_DIR / "data_clean"

# Nouveau dossier pour protéger les anciens vecteurs
DATA_VECTORS_DIR = BASE_DIR / "data_vectors_pages"

DATA_VECTORS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# PARAMÈTRES DU CHUNKING
# ============================================================

TAILLE_CHUNK = 500
OVERLAP = 100


# ============================================================
# FONCTION DE CHUNKING
# ============================================================

def decouper_texte(
    texte,
    taille=TAILLE_CHUNK,
    overlap=OVERLAP
):

    if taille <= 0 or overlap < 0 or overlap >= taille:
        raise ValueError(
            "La taille doit être positive et l'overlap "
            "doit être compris entre 0 et taille - 1."
        )

    chunks = []
    debut = 0

    while debut < len(texte):

        fin = debut + taille

        chunk = texte[debut:fin].strip()

        if chunk:
            chunks.append(chunk)

        if fin >= len(texte):
            break

        debut += taille - overlap

    return chunks


# ============================================================
# RÉCUPÉRATION DES JSON
# ============================================================

fichiers_json = sorted(
    DATA_CLEAN_DIR.glob("*.json")
)

print(
    f"Nombre de fichiers JSON trouvés : "
    f"{len(fichiers_json)}"
)


# ============================================================
# CHARGEMENT DU MODÈLE D'EMBEDDING
# ============================================================

print("\nChargement du modèle...")

modele = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Modèle chargé avec succès.")


# ============================================================
# TRAITEMENT DE TOUS LES DOCUMENTS
# ============================================================

nombre_documents = 0
nombre_chunks_total = 0
nombre_erreurs = 0


for fichier_json in fichiers_json:

    try:

        # ----------------------------------------------------
        # 1. LECTURE DU JSON
        # ----------------------------------------------------

        with open(
            fichier_json,
            "r",
            encoding="utf-8"
        ) as fichier:

            donnees = json.load(fichier)

        # ----------------------------------------------------
        # 2. CHUNKING AVEC CONSERVATION DES PAGES
        # ----------------------------------------------------

        chunks_avec_pages = []

        if (
            donnees["format"].lower() == ".pdf"
            and donnees.get("pages")
        ):

            # Chaque page est découpée séparément
            for page in donnees["pages"]:

                numero_page = page["numero_page"]
                texte_page = page["texte"]

                chunks_page = decouper_texte(
                    texte_page
                )

                for chunk in chunks_page:

                    chunks_avec_pages.append({
                        "texte": chunk,
                        "numero_page": numero_page
                    })

        else:

            # HTML et DOCX : pas de pagination PDF
            chunks_document = decouper_texte(
                donnees["texte"]
            )

            for chunk in chunks_document:

                chunks_avec_pages.append({
                    "texte": chunk,
                    "numero_page": None
                })

        if not chunks_avec_pages:
            raise ValueError(
                "Aucun chunk généré pour ce document."
            )

        # ----------------------------------------------------
        # 3. VECTORISATION
        # ----------------------------------------------------

        textes_chunks = [
            chunk["texte"]
            for chunk in chunks_avec_pages
        ]

        embeddings = modele.encode(
            textes_chunks,
            show_progress_bar=False
        )

        # ----------------------------------------------------
        # 4. CONSTRUCTION DES CHUNKS VECTORISÉS
        # ----------------------------------------------------

        chunks_vectorises = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks_avec_pages, embeddings)
        ):

            chunks_vectorises.append({
                "chunk_id": index,
                "texte": chunk["texte"],
                "numero_page": chunk["numero_page"],
                "embedding": embedding.tolist()
            })

        # ----------------------------------------------------
        # 5. STRUCTURE DU DOCUMENT FINAL
        # ----------------------------------------------------

        resultat = {
            "source": donnees["nom_fichier"],
            "format": donnees["format"],
            "date": donnees.get("date"),
            "taille_chunk": TAILLE_CHUNK,
            "overlap": OVERLAP,
            "nombre_chunks": len(chunks_vectorises),
            "dimension_embedding": 384,
            "modele_embedding": "all-MiniLM-L6-v2",
            "chunks": chunks_vectorises
        }

        # ----------------------------------------------------
        # 6. ENREGISTREMENT
        # ----------------------------------------------------

        chemin_sortie = (
            DATA_VECTORS_DIR /
            fichier_json.name
        )

        with open(
            chemin_sortie,
            "w",
            encoding="utf-8"
        ) as fichier:

            json.dump(
                resultat,
                fichier,
                ensure_ascii=False,
                indent=4
            )

        # ----------------------------------------------------
        # 7. COMPTEURS
        # ----------------------------------------------------

        nombre_documents += 1
        nombre_chunks_total += len(chunks_vectorises)

        print(
            f"[OK] {fichier_json.name} "
            f"-> {len(chunks_vectorises)} chunks"
        )

    except Exception as erreur:

        nombre_erreurs += 1

        print(
            f"[ERREUR] {fichier_json.name} "
            f"-> {erreur}"
        )


# ============================================================
# BILAN FINAL
# ============================================================

print("\n--- BILAN VECTORISATION ---")

print(
    f"Documents traités : {nombre_documents}"
)

print(
    f"Nombre total de chunks : {nombre_chunks_total}"
)

print(
    f"Erreurs : {nombre_erreurs}"
)

print(
    "Dimension des embeddings : 384"
)
