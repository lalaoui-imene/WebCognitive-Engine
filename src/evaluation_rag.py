
import csv
import re
from pathlib import Path
from datetime import datetime

from rag import rechercher_passages, generer_reponse


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
EVALUATION_DIR = BASE_DIR / "evaluation"
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# QUESTIONS DE TEST
# ============================================================

QUESTIONS = [
    "Qu'est-ce qu'un jumeau numérique en médecine ?",

    "Comment les jumeaux numériques peuvent-ils "
    "améliorer la médecine personnalisée ?",

    "Quelles sont les principales limites techniques, "
    "éthiques et cliniques des jumeaux numériques ?",

    "Comment les jumeaux numériques peuvent-ils "
    "aider à prédire les maladies ?",

    "Quels sont les enjeux de confidentialité "
    "des données médicales ?"
]


# ============================================================
# ANALYSE AUTOMATIQUE DES CITATIONS
# ============================================================

def analyser_citations(reponse, passages):

    numeros_cites = [
        int(n)
        for n in re.findall(
            r"\[Source\s+(\d+)\]",
            reponse,
            flags=re.IGNORECASE
        )
    ]

    numeros_valides = {
        p["numero"] for p in passages
    }

    citations_correctes = [
        n for n in numeros_cites
        if n in numeros_valides
    ]

    citations_incorrectes = [
        n for n in numeros_cites
        if n not in numeros_valides
    ]

    total = len(numeros_cites)

    taux_validite = (
        round(len(citations_correctes) / total * 100, 2)
        if total else 0
    )

    return {
        "nombre_citations": total,
        "citations_valides": len(citations_correctes),
        "citations_invalides": len(citations_incorrectes),
        "taux_validite_citations": taux_validite
    }


# ============================================================
# NOTATION HUMAINE
# ============================================================

def demander_note(critere):

    while True:

        note = input(
            f"{critere} (0, 1 ou 2) : "
        ).strip()

        if note in ("0", "1", "2"):
            return int(note)

        print("Veuillez saisir 0, 1 ou 2.")


# ============================================================
# ÉVALUATION
# ============================================================

def lancer_evaluation():

    resultats = []

    for numero, question in enumerate(QUESTIONS, start=1):

        print("\n" + "=" * 65)
        print(f"TEST {numero} / {len(QUESTIONS)}")
        print("=" * 65)

        print("\nQUESTION :", question)

        # Même recherche et même reranking que rag.py
        passages = rechercher_passages(question)

        print("\n--- SOURCES UTILISÉES PAR LE RAG ---")

        for passage in passages:

            print(f"\n[Source {passage['numero']}]")
            print("Document :", passage["source"])
            print("Chunk :", passage["chunk_id"])
            print("Extrait :", passage["texte"][:1200])

        # Même génération que rag.py
        print("\n--- RÉPONSE GÉNÉRÉE ---\n")

        reponse = generer_reponse(question, passages)

        print(reponse)

        # Vérification structurelle des citations
        citations = analyser_citations(reponse, passages)

        print("\n--- CONTRÔLE DES CITATIONS ---")
        print(
            "Nombre de citations :",
            citations["nombre_citations"]
        )
        print(
            "Citations avec un numéro existant :",
            citations["citations_valides"]
        )
        print(
            "Citations avec un numéro inexistant :",
            citations["citations_invalides"]
        )
        print(
            "Taux de validité des numéros :",
            f"{citations['taux_validite_citations']}%"
        )

        print("\n--- ÉVALUATION HUMAINE ---")
        print("0 = insuffisant")
        print("1 = partiel")
        print("2 = satisfaisant")

        pertinence = demander_note(
            "Pertinence de la réponse"
        )

        fidelite = demander_note(
            "Fidélité aux passages documentaires"
        )

        qualite_citations = demander_note(
            "Justification des affirmations par les citations"
        )

        clarte = demander_note(
            "Clarté et qualité du français"
        )

        note_totale = (
            pertinence
            + fidelite
            + qualite_citations
            + clarte
        )

        resultats.append({
            "test": numero,
            "question": question,
            "reponse": reponse,
            "pertinence": pertinence,
            "fidelite": fidelite,
            "qualite_citations": qualite_citations,
            "clarte": clarte,
            "note_sur_8": note_totale,
            "nombre_citations": citations["nombre_citations"],
            "citations_valides": citations["citations_valides"],
            "citations_invalides": citations["citations_invalides"],
            "taux_validite_citations": citations[
                "taux_validite_citations"
            ],
            "sources": " | ".join(
                f"[Source {p['numero']}] "
                f"{p['source']} (chunk {p['chunk_id']})"
                for p in passages
            ),
            "extraits": "\n\n".join(
                f"[Source {p['numero']}] "
                f"{p['texte'][:1200]}"
                for p in passages
            )
        })

        print(f"\nRésultat du test : {note_totale}/8")

    # ========================================================
    # EXPORT DES RÉSULTATS
    # ========================================================

    date = datetime.now().strftime("%Y%m%d_%H%M%S")

    fichier = (
        EVALUATION_DIR
        / f"evaluation_rag_corrigee_{date}.csv"
    )

    with open(
        fichier,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=resultats[0].keys(),
            delimiter=";"
        )

        writer.writeheader()
        writer.writerows(resultats)

    # ========================================================
    # BILAN GLOBAL
    # ========================================================

    moyenne = sum(
        r["note_sur_8"] for r in resultats
    ) / len(resultats)

    print("\n" + "=" * 65)
    print("BILAN FINAL DE L'ÉVALUATION RAG")
    print("=" * 65)

    print("Nombre de tests :", len(resultats))
    print(f"Note moyenne : {moyenne:.2f}/8")
    print(f"Score moyen : {moyenne / 8 * 100:.1f}%")
    print("\nFichier enregistré :", fichier)


if __name__ == "__main__":
    lancer_evaluation()
