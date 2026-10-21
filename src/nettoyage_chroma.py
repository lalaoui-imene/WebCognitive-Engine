
from pathlib import Path
import json
import chromadb

# ============================================================
# CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CLEAN_DIR = BASE_DIR / "data_clean"
DB_DIR = BASE_DIR / "chroma_db"

TAILLE_CHUNK = 500
OVERLAP = 100

# ============================================================
# CONNEXION CHROMADB
# ============================================================

client = chromadb.PersistentClient(path=str(DB_DIR))

collection = client.get_collection(
    name="webcognitive_documents"
)

print(f"Vecteurs avant nettoyage : {collection.count()}")

# ============================================================
# CALCUL DES IDENTIFIANTS ATTENDUS
# ============================================================

ids_attendus = set()

for fichier_json in sorted(DATA_CLEAN_DIR.glob("*.json")):

    with open(fichier_json, "r", encoding="utf-8") as f:
        donnees = json.load(f)

    texte = donnees["texte"]
    debut = 0
    index = 0

    while debut < len(texte):

        fin = min(debut + TAILLE_CHUNK, len(texte))
        chunk = texte[debut:fin].strip()

        if chunk:
            identifiant = f"{fichier_json.stem}_{index}"
            ids_attendus.add(identifiant)
            index += 1

        if fin == len(texte):
            break

        debut += TAILLE_CHUNK - OVERLAP

# ============================================================
# COMPARAISON AVEC CHROMADB
# ============================================================

ids_en_base = set(collection.get(include=[])["ids"])

ids_supplementaires = sorted(
    ids_en_base - ids_attendus
)

ids_manquants = sorted(
    ids_attendus - ids_en_base
)

print(f"Identifiants attendus : {len(ids_attendus)}")
print(f"Vecteurs supplémentaires : {len(ids_supplementaires)}")
print(f"Vecteurs manquants : {len(ids_manquants)}")

# ============================================================
# NETTOYAGE SÉCURISÉ
# ============================================================

if len(ids_supplementaires) == 11 and not ids_manquants:

    print("\nIdentifiants à supprimer :")

    for identifiant in ids_supplementaires:
        print(identifiant)

    confirmation = input(
        "\nConfirmer la suppression des 11 vecteurs ? (oui/non) : "
    )

    if confirmation.strip().lower() == "oui":

        collection.delete(ids=ids_supplementaires)

        print("\nNettoyage terminé !")
        print(f"Vecteurs restants : {collection.count()}")

    else:
        print("\nSuppression annulée.")

else:
    print(
        "\nAucune suppression effectuée : "
        "le résultat ne correspond pas aux 11 vecteurs attendus."
    )
