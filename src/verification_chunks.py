
from pathlib import Path
import json

# ============================================================
# CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CLEAN_DIR = BASE_DIR / "data_clean"
DATA_VECTORS_DIR = BASE_DIR / "data_vectors"


# ============================================================
# NOUVELLE FONCTION DE CHUNKING (API)
# ============================================================

def decouper_texte(texte, taille=500, overlap=100):

    chunks = []
    debut = 0

    while debut < len(texte):

        fin = min(debut + taille, len(texte))

        chunk = texte[debut:fin].strip()

        if chunk:
            chunks.append(chunk)

        if fin == len(texte):
            break

        debut += taille - overlap

    return chunks


# ============================================================
# COMPARAISON DES DOCUMENTS
# ============================================================

print("\n--- VÉRIFICATION DES CHUNKS ---")

total_anciens = 0
total_nouveaux = 0

for fichier in sorted(DATA_CLEAN_DIR.glob("*.json")):

    with open(fichier, "r", encoding="utf-8") as f:
        donnees = json.load(f)

    texte = donnees["texte"]

    nouveaux_chunks = decouper_texte(texte)

    fichier_vecteurs = DATA_VECTORS_DIR / fichier.name

    with open(fichier_vecteurs, "r", encoding="utf-8") as f:
        donnees_vecteurs = json.load(f)

    anciens_chunks = donnees_vecteurs["chunks"]

    total_anciens += len(anciens_chunks)
    total_nouveaux += len(nouveaux_chunks)

    difference = len(anciens_chunks) - len(nouveaux_chunks)

    if difference != 0:

        print(f"\nDocument : {fichier.name}")
        print(f"Anciens chunks : {len(anciens_chunks)}")
        print(f"Nouveaux chunks : {len(nouveaux_chunks)}")
        print(f"Différence : {difference}")

        print("Dernier chunk supplémentaire :")
        print(repr(anciens_chunks[-1]["texte"]))


# ============================================================
# BILAN
# ============================================================

print("\n--- BILAN COMPARAISON ---")
print(f"Anciens chunks : {total_anciens}")
print(f"Nouveaux chunks : {total_nouveaux}")
print(f"Différence totale : {total_anciens - total_nouveaux}")
