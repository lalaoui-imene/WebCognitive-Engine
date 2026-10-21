
from pathlib import Path
from collections import Counter
import re

import chromadb


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"

NOM_COLLECTION = "webcognitive_documents_pages"

MOTS_CLES = {
    "Jumeau numérique": [
        "digital twin",
        "digital twins",
        "jumeau numérique",
        "jumeaux numériques",
    ],
    "Médecine personnalisée": [
        "personalized medicine",
        "personalised medicine",
        "precision medicine",
        "médecine personnalisée",
        "médecine de précision",
    ],
    "Cardiologie": [
        "cardiology",
        "cardiovascular",
        "cardiac",
        "cardiologie",
        "cardiovasculaire",
    ],
    "Oncologie": [
        "oncology",
        "cancer",
        "tumor",
        "tumour",
        "oncologie",
    ],
    "Diagnostic": [
        "diagnosis",
        "diagnostic",
    ],
    "Traitement": [
        "treatment",
        "therapy",
        "therapeutic",
        "traitement",
    ],
    "Simulation": [
        "simulation",
        "simulations",
        "simulate",
    ],
    "Intelligence artificielle": [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "intelligence artificielle",
    ],
    "Éthique": [
        "ethics",
        "ethical",
        "éthique",
    ],
    "Validation clinique": [
        "clinical validation",
        "model validation",
        "validation clinique",
    ],
}


# ============================================================
# OUTILS
# ============================================================

def identifier_format(document):
    extension = Path(document).suffix.lower()

    if extension == ".pdf":
        return "PDF"
    if extension in (".html", ".htm"):
        return "HTML"
    if extension == ".docx":
        return "DOCX"

    return "Autre"


def compter_mots(texte):
    return len(re.findall(r"\b\w+\b", texte))


def contient_expression(texte, expression):
    motif = (
        r"(?<!\w)"
        + re.escape(expression.lower())
        + r"(?!\w)"
    )
    return re.search(motif, texte) is not None


# ============================================================
# ANALYSE
# ============================================================

def analyser_corpus():

    print("\n" + "=" * 60)
    print("WEBCOGNITIVE ENGINE - ÉTAPE 7")
    print("ANALYSE STATISTIQUE DU CORPUS")
    print("=" * 60)

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_collection(
        name=NOM_COLLECTION
    )

    resultats = collection.get(
        include=["documents", "metadatas"]
    )

    textes = resultats["documents"]
    metadonnees = resultats["metadatas"]

    chunks_par_document = Counter()
    formats = Counter()
    tailles_mots = []
    tailles_caracteres = []

    # Nombre de chunks contenant chaque thématique
    mots_cles_chunks = Counter()

    # Documents distincts contenant chaque thématique
    mots_cles_documents = {
        theme: set()
        for theme in MOTS_CLES
    }

    documents_distincts = set()

    for texte, metadata in zip(textes, metadonnees):

        metadata = metadata or {}

        source = str(
            metadata.get("source", "Source inconnue")
        )

        documents_distincts.add(source)
        chunks_par_document[source] += 1

        texte = texte or ""

        tailles_mots.append(compter_mots(texte))
        tailles_caracteres.append(len(texte))

        texte_minuscule = texte.lower()

        for theme, expressions in MOTS_CLES.items():

            if any(
                contient_expression(
                    texte_minuscule,
                    expression
                )
                for expression in expressions
            ):
                mots_cles_chunks[theme] += 1
                mots_cles_documents[theme].add(source)

    for source in documents_distincts:
        formats[identifier_format(source)] += 1

    nombre_documents = len(documents_distincts)
    nombre_chunks = len(textes)

    # ========================================================
    # INDICATEURS GÉNÉRAUX
    # ========================================================

    print("\n--- INDICATEURS GÉNÉRAUX ---")

    print("Documents indexés :", nombre_documents)
    print("Chunks indexés :", nombre_chunks)

    if nombre_documents:
        print(
            "Moyenne de chunks par document :",
            round(nombre_chunks / nombre_documents, 2)
        )

    # ========================================================
    # FORMATS
    # ========================================================

    print("\n--- RÉPARTITION PAR FORMAT ---")

    for format_document, nombre in formats.most_common():

        pourcentage = (
            nombre / nombre_documents * 100
            if nombre_documents
            else 0
        )

        print(
            f"{format_document} : {nombre} "
            f"({pourcentage:.1f} %)"
        )

    # ========================================================
    # TAILLE DES CHUNKS
    # ========================================================

    print("\n--- TAILLE DES CHUNKS ---")

    if tailles_mots:

        print(
            "Taille minimale (mots) :",
            min(tailles_mots)
        )

        print(
            "Taille maximale (mots) :",
            max(tailles_mots)
        )

        print(
            "Taille moyenne (mots) :",
            round(
                sum(tailles_mots) / len(tailles_mots),
                2
            )
        )

        print(
            "Taille moyenne (caractères) :",
            round(
                sum(tailles_caracteres)
                / len(tailles_caracteres),
                2
            )
        )

        tranches = {
            "Moins de 100 mots": 0,
            "100 à 199 mots": 0,
            "200 à 299 mots": 0,
            "300 à 499 mots": 0,
            "500 mots et plus": 0,
        }

        for taille in tailles_mots:

            if taille < 100:
                tranches["Moins de 100 mots"] += 1

            elif taille < 200:
                tranches["100 à 199 mots"] += 1

            elif taille < 300:
                tranches["200 à 299 mots"] += 1

            elif taille < 500:
                tranches["300 à 499 mots"] += 1

            else:
                tranches["500 mots et plus"] += 1

        print("\nDistribution des tailles :")

        for tranche, nombre in tranches.items():
            print(f"{tranche} : {nombre} chunks")

    # ========================================================
    # FRÉQUENCE DES THÉMATIQUES
    # ========================================================

    print("\n--- FRÉQUENCE DES THÉMATIQUES ---")
    print(
        "Une thématique est comptée une seule fois "
        "par chunk, même si plusieurs synonymes "
        "sont présents."
    )

    for theme, nombre in mots_cles_chunks.most_common():

        nb_documents = len(
            mots_cles_documents[theme]
        )

        print(
            f"{theme} : "
            f"{nombre} chunks | "
            f"{nb_documents} documents"
        )

    # ========================================================
    # DOCUMENTS LES PLUS VOLUMINEUX
    # ========================================================

    print("\n--- TOP 10 DOCUMENTS PAR NOMBRE DE CHUNKS ---")

    for source, nombre in chunks_par_document.most_common(10):

        print(f"{source} : {nombre} chunks")

    print("\nAnalyse terminée avec succès !")


# ============================================================
# EXÉCUTION
# ============================================================

if __name__ == "__main__":
    analyser_corpus()
