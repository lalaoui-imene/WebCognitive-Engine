
import csv
import re
from pathlib import Path
from datetime import datetime

from recherche import rechercher_passages


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTATS_DIR = BASE_DIR / "evaluation"

RESULTATS_DIR.mkdir(parents=True, exist_ok=True)

TOP_K = 5


# ============================================================
# QUESTIONS DE TEST
# ============================================================

QUESTIONS = [
    {
        "id": 1,
        "question": "Qu'est-ce qu'un jumeau numérique en médecine ?",
        "requete": (
            "What is a medical digital twin? "
            "Definition and explanation of digital twins "
            "in healthcare."
        ),
        "mots_cles": [
            "digital twin",
            "virtual",
            "patient",
            "model"
        ]
    },
    {
        "id": 2,
        "question": (
            "Comment les jumeaux numériques peuvent-ils "
            "améliorer la médecine personnalisée ?"
        ),
        "requete": (
            "Benefits and applications of digital twins "
            "in personalized medicine, diagnosis, "
            "monitoring and treatment."
        ),
        "mots_cles": [
            "personalized",
            "treatment",
            "patient",
            "prediction"
        ]
    },
    {
        "id": 3,
        "question": (
            "Quelles sont les principales limites techniques, "
            "éthiques et cliniques des jumeaux numériques ?"
        ),
        "requete": (
            "Limitations and challenges of digital twins "
            "in healthcare: clinical validation, "
            "privacy, interoperability and ethics."
        ),
        "mots_cles": [
            "validation",
            "privacy",
            "ethical",
            "challenge"
        ]
    },
    {
        "id": 4,
        "question": (
            "Comment les jumeaux numériques peuvent-ils "
            "aider à prédire les maladies ?"
        ),
        "requete": (
            "Digital twins for disease prediction, "
            "risk assessment and preventive healthcare."
        ),
        "mots_cles": [
            "prediction",
            "disease",
            "risk",
            "patient"
        ]
    },
    {
        "id": 5,
        "question": (
            "Quels sont les enjeux de confidentialité "
            "des données médicales ?"
        ),
        "requete": (
            "Data privacy, security and ethical concerns "
            "of digital twins in healthcare."
        ),
        "mots_cles": [
            "privacy",
            "security",
            "data",
            "ethical"
        ]
    }
]


# ============================================================
# ÉVALUATION DES PASSAGES RETROUVÉS
# ============================================================

def evaluer_passages(passages, mots_cles):

    if not passages:
        return {
            "precision_indicative": 0.0,
            "couverture_mots_cles": 0.0,
            "diversite_sources": 0,
            "nombre_passages": 0
        }

    textes = [
        passage["texte"].lower()
        for passage in passages
    ]

    # Indicateur heuristique :
    # un passage est considéré comme pertinent
    # s'il contient au moins un mot-clé attendu.
    passages_avec_mot_cle = sum(
        any(mot.lower() in texte for mot in mots_cles)
        for texte in textes
    )

    precision_indicative = (
        passages_avec_mot_cle / len(passages)
    )

    texte_global = " ".join(textes)

    mots_presents = sum(
        mot.lower() in texte_global
        for mot in mots_cles
    )

    couverture = (
        mots_presents / len(mots_cles)
        if mots_cles else 0.0
    )

    sources = {
        passage["source"]
        for passage in passages
    }

    return {
        "precision_indicative": round(
            precision_indicative, 3
        ),
        "couverture_mots_cles": round(
            couverture, 3
        ),
        "diversite_sources": len(sources),
        "nombre_passages": len(passages)
    }


# ============================================================
# LANCEMENT DE L'ÉVALUATION
# ============================================================

def lancer_evaluation():

    resultats = []

    print("\n" + "=" * 60)
    print("ÉVALUATION DU MOTEUR WEBCOGNITIVE")
    print("=" * 60)

    for test in QUESTIONS:

        print(f"\nTEST {test['id']}")
        print("Question :", test["question"])

        passages = rechercher_passages(
            test["requete"],
            top_k=TOP_K
        )

        mesures = evaluer_passages(
            passages,
            test["mots_cles"]
        )

        print(
            "Pertinence indicative :",
            f"{mesures['precision_indicative']:.0%}"
        )

        print(
            "Couverture des mots-clés :",
            f"{mesures['couverture_mots_cles']:.0%}"
        )

        print(
            "Documents différents :",
            mesures["diversite_sources"]
        )

        resultats.append({
            "id": test["id"],
            "question": test["question"],
            **mesures,
            "sources": " | ".join(
                passage["source"]
                for passage in passages
            )
        })

    # ========================================================
    # EXPORT CSV
    # ========================================================

    date_execution = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    chemin_csv = (
        RESULTATS_DIR /
        f"evaluation_{date_execution}.csv"
    )

    with open(
        chemin_csv,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as fichier:

        writer = csv.DictWriter(
            fichier,
            fieldnames=resultats[0].keys(),
            delimiter=";"
        )

        writer.writeheader()
        writer.writerows(resultats)

    # ========================================================
    # BILAN GLOBAL
    # ========================================================

    moyenne_pertinence = sum(
        r["precision_indicative"]
        for r in resultats
    ) / len(resultats)

    moyenne_couverture = sum(
        r["couverture_mots_cles"]
        for r in resultats
    ) / len(resultats)

    print("\n" + "=" * 60)
    print("BILAN GLOBAL")
    print("=" * 60)

    print(
        "Pertinence indicative moyenne :",
        f"{moyenne_pertinence:.1%}"
    )

    print(
        "Couverture moyenne des mots-clés :",
        f"{moyenne_couverture:.1%}"
    )

    print("\nRésultats enregistrés dans :")
    print(chemin_csv)


# ============================================================
# EXÉCUTION
# ============================================================

if __name__ == "__main__":
    lancer_evaluation()
