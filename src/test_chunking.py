from pathlib import Path
import json


# ============================================================
# CHEMIN DES DONNÉES
# ============================================================

DATA_CLEAN_DIR = Path(__file__).resolve().parent.parent / "data_clean"


# ============================================================
# FONCTION DE CHUNKING
# ============================================================

def decouper_texte(texte, taille, overlap):

    chunks = []
    debut = 0

    while debut < len(texte):

        fin = debut + taille

        chunk = texte[debut:fin].strip()

        if chunk:
            chunks.append(chunk)

        debut += taille - overlap

    return chunks


# ============================================================
# CHARGEMENT D'UN DOCUMENT TEST
# ============================================================

fichiers_json = sorted(DATA_CLEAN_DIR.glob("*.json"))

fichier_test = fichiers_json[0]

with open(
    fichier_test,
    "r",
    encoding="utf-8"
) as fichier:

    donnees = json.load(fichier)

texte = donnees["texte"]


# ============================================================
# TEST DE PLUSIEURS TAILLES
# ============================================================

tests = [
    (300, 60),
    (500, 100),
    (700, 140)
]


print(f"Document testé : {fichier_test.name}")
print(f"Longueur du texte : {len(texte)} caractères")

print("\n--- COMPARAISON DES STRATÉGIES ---")


for taille, overlap in tests:

    chunks = decouper_texte(
        texte,
        taille,
        overlap
    )

    longueurs = [
        len(chunk)
        for chunk in chunks
    ]

    moyenne = sum(longueurs) / len(longueurs)

    print(
        f"\nTaille : {taille} caractères"
    )

    print(
        f"Overlap : {overlap} caractères"
    )

    print(
        f"Nombre de chunks : {len(chunks)}"
    )

    print(
        f"Taille moyenne : {moyenne:.2f} caractères"
    )