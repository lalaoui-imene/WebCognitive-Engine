
from pathlib import Path
import re
import unicodedata

import requests
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"

MODELE_EMBEDDING = "all-MiniLM-L6-v2"
MODELE_RERANKING = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MODELE_LLM = "qwen2.5:7b"

NOM_COLLECTION = "webcognitive_documents_pages"
URL_OLLAMA = "http://127.0.0.1:11434/api/chat"

TOP_K_CANDIDATS = 40
TOP_K_FINAL = 5
TOP_K_DIVERSIFICATION = 30
ECART_SCORE_MAX = 3.0

LONGUEUR_MIN_PASSAGE = 180
LONGUEUR_CONTEXTE = 850

TIMEOUT_OLLAMA = 360
NUM_CTX = 4096
NUM_PREDICT = 650


# ============================================================
# CHARGEMENT DES MODELES
# ============================================================

print("Connexion à ChromaDB...")

client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_collection(name=NOM_COLLECTION)

print(
    f"Collection : {NOM_COLLECTION} "
    f"({collection.count()} vecteurs)"
)

print("Chargement du modèle d'embedding...")
modele_embedding = SentenceTransformer(MODELE_EMBEDDING)

print("Chargement du modèle de reranking...")
modele_reranking = CrossEncoder(MODELE_RERANKING)

print("Modèles chargés avec succès.")


# ============================================================
# ANALYSE DE LA QUESTION
# ============================================================

def normaliser_texte(texte):
    texte = unicodedata.normalize("NFD", str(texte).lower())
    return "".join(
        caractere
        for caractere in texte
        if unicodedata.category(caractere) != "Mn"
    )


def contient_expression(texte, expression):
    texte = normaliser_texte(texte)
    expression = normaliser_texte(expression)

    motif = r"(?<!\w)" + re.escape(expression) + r"(?!\w)"
    return re.search(motif, texte) is not None


def analyser_question(question):
    themes = {
        "definition": [
            "qu'est-ce", "definition", "definir",
            "c'est quoi", "que signifie"
        ],
        "applications": [
            "application", "applications", "utilisation",
            "utilise", "utiliser", "usage",
            "cas concret", "exemple", "comment"
        ],
        "diagnostic": [
            "diagnostic", "diagnostiquer",
            "detection", "detecter"
        ],
        "traitement": [
            "traitement", "traitements", "therapie",
            "therapeutique", "personnaliser",
            "personnalise", "personnalisee",
            "individualise", "medecine personnalisee"
        ],
        "suivi": [
            "suivi", "surveillance", "monitoring",
            "evolution du patient"
        ],
        "prediction": [
            "prediction", "predire", "anticiper",
            "prevention", "risque de maladie"
        ],
        "limites": [
            "limite", "limites", "obstacle",
            "difficulte", "defi", "barriere",
            "risque", "frein", "probleme",
            "contraintes"
        ],
        "ethique": [
            "ethique", "confidentialite",
            "vie privee", "protection des donnees",
            "consentement", "biais algorithmique"
        ],
        "benefices": [
            "avantage", "avantages", "benefice",
            "benefices", "apport", "apports",
            "ameliorer", "interet", "utilite"
        ]
    }

    aspects = []

    for aspect, mots_cles in themes.items():
        if any(
            contient_expression(question, mot)
            for mot in mots_cles
        ):
            aspects.append(aspect)

    return aspects or ["general"]


def identifier_specialite(question):
    specialites = {
        "cardiology and cardiovascular medicine": [
            "cardiologie", "cardiaque",
            "cardiovasculaire", "coeur", "arythmie"
        ],
        "oncology and cancer care": [
            "oncologie", "cancer", "tumeur"
        ],
        "neurology and brain disorders": [
            "neurologie", "cerveau", "neurologique"
        ],
        "diabetes and endocrinology": [
            "diabete", "diabetique", "endocrinologie"
        ],
        "surgery and surgical planning": [
            "chirurgie", "chirurgical", "operation"
        ]
    }

    for specialite, mots in specialites.items():
        if any(
            contient_expression(question, mot)
            for mot in mots
        ):
            return specialite

    return "healthcare and personalized medicine"


# ============================================================
# REFORMULATION MULTI-ASPECTS
# ============================================================

def reformuler_question(question):
    aspects = analyser_question(question)
    specialite = identifier_specialite(question)

    formulations = {
        "definition": (
            "Definition of medical digital twins, "
            "virtual patient or organ models updated "
            "using real-world clinical data."
        ),
        "applications": (
            "Clinical applications of patient-specific "
            "digital twins, medical use cases, "
            "simulations and clinical decision support."
        ),
        "diagnostic": (
            "Medical digital twins for personalized "
            "diagnosis, disease detection and "
            "patient-specific clinical assessment."
        ),
        "traitement": (
            "Digital twins for personalized treatment "
            "planning, therapy optimization, simulation "
            "of therapeutic interventions and "
            "patient-specific treatment response."
        ),
        "suivi": (
            "Digital twins for patient monitoring, "
            "longitudinal follow-up and disease "
            "progression assessment."
        ),
        "prediction": (
            "Predictive digital twins for disease "
            "progression, risk assessment and "
            "preventive medicine."
        ),
        "limites": (
            "Clinical limitations of medical digital "
            "twins, model validation, interoperability, "
            "computational requirements, clinical "
            "adoption and regulatory challenges."
        ),
        "ethique": (
            "Ethical challenges of medical digital "
            "twins, patient privacy, consent, "
            "algorithmic bias and data protection."
        ),
        "benefices": (
            "Benefits of digital twins for precision "
            "medicine, individualized patient care, "
            "diagnosis and treatment outcomes."
        ),
        "general": (
            "Medical digital twins in healthcare, "
            "clinical applications and personalized medicine."
        )
    }

    return [
        {
            "aspect": aspect,
            "requete": f"{specialite}. {formulations[aspect]}"
        }
        for aspect in aspects
    ]


# ============================================================
# NETTOYAGE DES PASSAGES
# ============================================================

def nettoyer_espaces(texte):
    return re.sub(r"\s+", " ", str(texte)).strip()


def est_reference_bibliographique(ligne):
    ligne = nettoyer_espaces(ligne)

    if not ligne:
        return False

    ligne_min = ligne.lower()

    if re.match(r"^\[\d{1,3}\]\s+", ligne):
        return True

    if re.match(r"^\d{1,3}[.)]\s+", ligne):
        if (
            re.search(r"\b(19|20)\d{2}\b", ligne)
            or "doi" in ligne_min
            or "http" in ligne_min
        ):
            return True

    if re.search(r"https?://(?:dx\.)?doi\.org/", ligne_min):
        return True

    if re.search(r"\bdoi\s*:\s*10\.\d{4,9}/", ligne_min):
        return True

    if len(re.findall(r"https?://|www\.", ligne_min)) >= 2:
        return True

    return False


def nettoyer_passage(texte):
    if not texte:
        return ""

    texte = str(texte).replace("\x00", " ").strip()

    lignes = [
        ligne.strip()
        for ligne in texte.splitlines()
        if ligne.strip()
    ]

    lignes_utiles = []

    for ligne in lignes:
        ligne_min = ligne.lower().strip()

        if re.match(
            r"^(references|bibliography|références|bibliographie)"
            r"\s*:?\s*$",
            ligne_min
        ):
            break

        if est_reference_bibliographique(ligne):
            continue

        lignes_utiles.append(ligne)

    return nettoyer_espaces(" ".join(lignes_utiles))


def score_bibliographique(texte):
    texte_min = normaliser_texte(texte)

    indices = [
        "references", "bibliography",
        "available online", "available from",
        "accessed on", "accessed september",
        "accessed october", "accessed november",
        "accessed december", "crossref",
        "pubmed", "researchgate.net/publication/",
        "doi.org/", "isbn"
    ]

    score = sum(
        texte_min.count(indice)
        for indice in indices
    )

    score += 2 * len(
        re.findall(
            r"https?://|www\.|10\.\d{4,9}/",
            texte_min
        )
    )

    if texte.count(";") >= 8:
        score += 2

    return score


def passage_exploitable(texte):
    if not texte:
        return False

    texte_original = str(texte).strip()

    if len(texte_original) < LONGUEUR_MIN_PASSAGE:
        return False

    texte_min = normaliser_texte(texte_original)

    if re.match(
        r"^(references|bibliography|bibliographie)\b",
        texte_min
    ):
        return False

    if score_bibliographique(texte_original) >= 5:
        return False

    texte_nettoye = nettoyer_passage(texte_original)

    if len(texte_nettoye) < LONGUEUR_MIN_PASSAGE:
        return False

    mots = re.findall(r"[a-zA-ZÀ-ÿ]+", texte_nettoye)

    if len(mots) < 35:
        return False

    if len(texte_nettoye) < 0.55 * len(texte_original):
        return False

    if score_bibliographique(texte_nettoye) >= 4:
        return False

    return True


# ============================================================
# RECHERCHE SEMANTIQUE MULTI-ASPECTS
# ============================================================

def rechercher_candidats(question):
    requetes = reformuler_question(question)
    nombre_vecteurs = collection.count()

    if nombre_vecteurs == 0:
        return [], requetes

    candidats = {}

    print("\nAspects recherchés :")

    for element in requetes:
        aspect = element["aspect"]
        requete = element["requete"]

        print(f" - {aspect} : {requete}")

        vecteur = modele_embedding.encode(requete).tolist()

        resultats = collection.query(
            query_embeddings=[vecteur],
            n_results=min(TOP_K_CANDIDATS, nombre_vecteurs),
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        textes = resultats["documents"][0]
        metadonnees = resultats["metadatas"][0]
        distances = resultats["distances"][0]

        for i, texte in enumerate(textes):
            if not passage_exploitable(texte):
                continue

            metadata = metadonnees[i] or {}

            source = metadata.get(
                "source", "Source inconnue"
            )

            chunk_id = metadata.get("chunk_id", i)
            numero_page = metadata.get("numero_page")

            texte_nettoye = nettoyer_passage(texte)

            cle = (
                str(source),
                str(chunk_id),
                str(numero_page)
            )

            if cle not in candidats:
                candidats[cle] = {
                    "texte": texte_nettoye,
                    "source": source,
                    "chunk_id": chunk_id,
                    "numero_page": numero_page,
                    "distance": float(distances[i]),
                    "aspects": set(),
                    "scores_aspects": {}
                }

            candidats[cle]["aspects"].add(aspect)

            candidats[cle]["distance"] = min(
                candidats[cle]["distance"],
                float(distances[i])
            )

    print(f"\nCandidats exploitables : {len(candidats)}")

    return list(candidats.values()), requetes


# ============================================================
# RERANKING PAR ASPECT
# ============================================================

def reranker_candidats(candidats, requetes):
    if not candidats:
        return []

    for element in requetes:
        aspect = element["aspect"]
        requete = element["requete"]

        passages_concernes = [
            passage
            for passage in candidats
            if aspect in passage["aspects"]
        ]

        if not passages_concernes:
            continue

        paires = [
            (requete, passage["texte"])
            for passage in passages_concernes
        ]

        scores = modele_reranking.predict(paires)

        for passage, score in zip(
            passages_concernes, scores
        ):
            passage["scores_aspects"][aspect] = float(score)

    for passage in candidats:
        scores = passage["scores_aspects"]

        passage["score_reranking"] = (
            max(scores.values())
            if scores
            else -100.0
        )

    candidats.sort(
        key=lambda p: p["score_reranking"],
        reverse=True
    )

    return candidats


# ============================================================
# SELECTION EQUILIBREE DES SOURCES
# ============================================================

def diversifier_passages(passages, aspects=None):
    if not passages:
        return []

    aspects = aspects or []

    meilleur_score = passages[0]["score_reranking"]

    candidats = [
        passage
        for passage in passages
        if (
            meilleur_score - passage["score_reranking"]
            <= ECART_SCORE_MAX
        )
    ]

    candidats = candidats[:TOP_K_DIVERSIFICATION]

    selection = []
    documents_vus = set()
    passages_vus = set()

    def ajouter(passage):
        identifiant = (
            passage["source"],
            str(passage["chunk_id"]),
            str(passage.get("numero_page"))
        )

        if identifiant in passages_vus:
            return False

        if not passage_exploitable(passage["texte"]):
            return False

        selection.append(passage)
        passages_vus.add(identifiant)
        documents_vus.add(passage["source"])

        return True

    # Couverture des différents aspects
    for aspect in aspects:
        if len(selection) >= TOP_K_FINAL:
            break

        passages_aspect = [
            passage
            for passage in candidats
            if aspect in passage["scores_aspects"]
        ]

        passages_aspect.sort(
            key=lambda p: p["scores_aspects"][aspect],
            reverse=True
        )

        trouve = False

        for passage in passages_aspect:
            if passage["source"] not in documents_vus:
                if ajouter(passage):
                    trouve = True
                    break

        if not trouve:
            for passage in passages_aspect:
                if ajouter(passage):
                    break

    # Diversité documentaire
    for passage in candidats:
        if len(selection) >= TOP_K_FINAL:
            break

        if passage["source"] not in documents_vus:
            ajouter(passage)

    # Complément avec les meilleurs passages
    for passage in candidats:
        if len(selection) >= TOP_K_FINAL:
            break

        ajouter(passage)

    selection.sort(
        key=lambda p: p["score_reranking"],
        reverse=True
    )

    for i, passage in enumerate(selection):
        passage["numero"] = i + 1

    return selection


# ============================================================
# PIPELINE DE RECHERCHE
# ============================================================

def rechercher_passages(question):
    candidats, requetes = rechercher_candidats(question)

    if not candidats:
        return []

    candidats = reranker_candidats(
        candidats, requetes
    )

    aspects = [
        element["aspect"]
        for element in requetes
    ]

    passages_finaux = diversifier_passages(
        candidats, aspects
    )

    print("\nAspects identifiés :", aspects)

    print(
        "Documents distincts sélectionnés :",
        len({
            passage["source"]
            for passage in passages_finaux
        })
    )

    return passages_finaux


# ============================================================
# CONSTRUCTION DU CONTEXTE DOCUMENTAIRE
# ============================================================

def construire_contexte(passages):
    blocs = []

    for passage in passages:
        numero_page = passage.get("numero_page")

        indication_page = ""

        if numero_page is not None:
            indication_page = (
                f"Page du PDF : {numero_page}\n"
            )

        blocs.append(
            f"[Source {passage['numero']}]\n"
            f"Document : {passage['source']}\n"
            f"{indication_page}"
            f"Passage documentaire :\n"
            f"{passage['texte'][:LONGUEUR_CONTEXTE]}"
        )

    return "\n\n".join(blocs)


# ============================================================
# NORMALISATION DES CITATIONS
# ============================================================

def normaliser_citations(reponse, passages):
    numeros_valides = {
        int(passage["numero"])
        for passage in passages
    }

    def citation_valide(numero):
        numero = int(numero)

        if numero in numeros_valides:
            return f"[Source {numero}]"

        return "[citation non vérifiée]"

    def remplacer_plage(match):
        debut = int(match.group(1))
        fin = int(match.group(2))

        if fin < debut or fin - debut > 20:
            return "[citation non vérifiée]"

        return " ".join(
            citation_valide(numero)
            for numero in range(debut, fin + 1)
        )

    reponse = re.sub(
        r"\[\s*Sources?\s+(\d+)\s*[-–—]\s*(\d+)\s*\]",
        remplacer_plage,
        reponse,
        flags=re.IGNORECASE
    )

    def remplacer_liste(match):
        numeros = re.findall(r"\d+", match.group(1))

        return " ".join(
            citation_valide(numero)
            for numero in numeros
        )

    reponse = re.sub(
        r"\[\s*Sources?\s+"
        r"((?:\d+\s*(?:,|;|et|&)\s*)+\d+)"
        r"\s*\]",
        remplacer_liste,
        reponse,
        flags=re.IGNORECASE
    )

    reponse = re.sub(
        r"\[\s*Sources?\s+(\d+)\s*\]",
        lambda m: citation_valide(m.group(1)),
        reponse,
        flags=re.IGNORECASE
    )

    reponse = re.sub(
        r"(\[Source \d+\])(?:\s+\1)+",
        r"\1",
        reponse
    )

    # Suppression des paragraphes composés uniquement
    # de citations
    paragraphes = re.split(r"\n\s*\n", reponse)

    paragraphes_propres = []

    for paragraphe in paragraphes:
        paragraphe = paragraphe.strip()

        if not paragraphe:
            continue

        sans_citations = re.sub(
            r"\[Source \d+\]",
            "",
            paragraphe
        ).strip()

        if not sans_citations:
            continue

        paragraphes_propres.append(paragraphe)

    reponse = "\n\n".join(paragraphes_propres)

    reponse = re.sub(
        r"[ \t]+",
        " ",
        reponse
    ).strip()

    return reponse


# ============================================================
# CONTROLE DE LA REPONSE
# ============================================================

def reponse_complete(reponse, done_reason=None):
    """
    Vérifie si la réponse paraît terminée.

    done_reason='length' indique qu'Ollama a atteint
    sa limite de génération.
    """

    if not reponse or not reponse.strip():
        return False

    if done_reason == "length":
        return False

    texte = reponse.strip()

    # Retirer les citations placées à la fin
    texte = re.sub(
        r"(?:\s*\[Source \d+\])+\s*$",
        "",
        texte
    ).strip()

    # Retirer les éventuels marqueurs Markdown finaux
    texte = re.sub(r"[\s*_#]+$", "", texte).strip()

    # Une phrase complète se termine normalement ainsi
    return texte.endswith((".", "!", "?", "»", ")"))


def nettoyer_reponse_finale(reponse):
    """
    Nettoyage léger, sans modifier le sens.
    """

    reponse = reponse.strip()

    # Suppression d'éventuelles balises de réflexion
    reponse = re.sub(
        r"<think>.*?</think>",
        "",
        reponse,
        flags=re.DOTALL | re.IGNORECASE
    ).strip()

    # Harmoniser les titres Markdown
    reponse = re.sub(
        r"(?m)^\s*#{1,6}\s*",
        "**",
        reponse
    )

    # Ne pas supprimer les paragraphes
    reponse = re.sub(r"\n{3,}", "\n\n", reponse)

    return reponse.strip()


# ============================================================
# APPEL AU MODELE OLLAMA
# ============================================================

def appeler_ollama(
    prompt_systeme,
    prompt_utilisateur,
    num_predict=NUM_PREDICT
):
    response = requests.post(
        URL_OLLAMA,
        json={
            "model": MODELE_LLM,
            "messages": [
                {
                    "role": "system",
                    "content": prompt_systeme
                },
                {
                    "role": "user",
                    "content": prompt_utilisateur
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": num_predict,
                "num_ctx": NUM_CTX
            }
        },
        timeout=TIMEOUT_OLLAMA
    )

    response.raise_for_status()

    resultat = response.json()

    reponse = (
        resultat.get("message", {})
        .get("content", "")
        .strip()
    )

    done_reason = resultat.get("done_reason")

    return reponse, done_reason


# ============================================================
# GENERATION DE LA REPONSE
# ============================================================

def generer_reponse(question, passages):
    if not passages:
        return (
            "Je n'ai pas trouvé de passages suffisamment "
            "pertinents dans le corpus documentaire pour "
            "répondre à cette question."
        )

    contexte = construire_contexte(passages)

    aspects = analyser_question(question)

    question_multi_aspects = all(
        aspect in aspects
        for aspect in [
            "diagnostic",
            "suivi",
            "traitement",
            "limites"
        ]
    )

    prompt_systeme = """
Tu es un assistant scientifique spécialisé dans les
jumeaux numériques appliqués à la médecine.

Tu réponds uniquement à partir des extraits documentaires
fournis par le système RAG.

RÈGLES OBLIGATOIRES :

1. Rédige exclusivement en français.

2. Reformule les informations des sources en français.
   Ne recopie jamais une phrase entière en anglais.

3. Réponds directement à la question.

4. Utilise un style scientifique, précis et accessible.

5. Sois synthétique. Évite les longues introductions,
   les répétitions et les développements inutiles.

6. Cite les sources sous la forme [Source 1],
   [Source 2], etc., immédiatement après les
   informations qu'elles soutiennent.

7. Une citation doit correspondre à une information
   réellement présente dans l'extrait associé.

8. Ne cite pas une source uniquement pour augmenter
   le nombre de références.

9. N'invente aucune donnée médicale, étude,
   statistique ou efficacité clinique.

10. Distingue les possibilités théoriques des
    applications cliniquement validées.

11. Si les sources ne documentent pas suffisamment
    un point, indique-le clairement.

12. Termine toujours ta réponse par une phrase complète.

13. Ne reproduis pas les références bibliographiques
    présentes dans les extraits.

14. N'ajoute pas de liste de toutes les sources à la fin.

15. Ne dépasse pas la longueur demandée.

IMPORTANT :
La priorité est une réponse courte, complète,
fidèle aux documents et correctement citée.
"""

    if question_multi_aspects:
        consigne_structure = """
Réponds en QUATRE paragraphes courts, dans cet ordre :

**Diagnostic :**
Deux phrases maximum.

**Suivi des patients :**
Deux phrases maximum.

**Personnalisation des traitements :**
Deux phrases maximum.

**Limites actuelles :**
Trois phrases maximum.

Longueur totale : environ 160 à 210 mots.

Ne rédige ni introduction ni conclusion supplémentaire.
Ne développe pas une rubrique si les sources
ne permettent pas de la documenter.
"""
    else:
        consigne_structure = """
Réponds en deux à quatre courts paragraphes,
selon les aspects réellement demandés.

Longueur totale : environ 100 à 160 mots.

N'ajoute pas de rubriques étrangères à la question.
"""

    prompt_utilisateur = f"""
QUESTION :
{question}

DOCUMENTS :
{contexte}

FORMAT ATTENDU :
{consigne_structure}

RAPPELS :
- Répondre uniquement en français.
- Reformuler plutôt que recopier.
- Citer uniquement les sources qui soutiennent
  directement les affirmations.
- Ne pas dépasser la longueur indiquée.
- Terminer par une phrase complète.

RÉPONSE :
"""

    try:
        reponse, done_reason = appeler_ollama(
            prompt_systeme,
            prompt_utilisateur,
            num_predict=NUM_PREDICT
        )

        if not reponse:
            return "Le modèle n'a pas généré de réponse."

        print(
            "\nFin de génération Ollama :",
            done_reason
        )

        # Si la génération a été interrompue,
        # recommencer avec une consigne plus concise.
        if not reponse_complete(reponse, done_reason):
            print(
                "[ATTENTION] Réponse incomplète. "
                "Nouvelle tentative plus concise..."
            )

            prompt_court = f"""
QUESTION :
{question}

DOCUMENTS :
{contexte}

Rédige une réponse finale complète en français.

CONTRAINTES STRICTES :
- Maximum 130 mots.
- Phrases courtes.
- Aucune citation en anglais.
- Références [Source N] après les affirmations.
- Pas d'introduction générale.
- Pas de conclusion supplémentaire.
- Ne termine jamais au milieu d'une phrase.

Traite les aspects demandés par la question.
Si un aspect n'est pas documenté, signale-le.

RÉPONSE :
"""

            reponse_courte, raison_courte = appeler_ollama(
                prompt_systeme,
                prompt_court,
                num_predict=NUM_PREDICT
            )

            if reponse_complete(
                reponse_courte,
                raison_courte
            ):
                reponse = reponse_courte
            else:
                print(
                    "[ATTENTION] La seconde tentative "
                    "n'est pas entièrement terminée."
                )

                # Ne conserver que les phrases complètes
                # de la meilleure réponse disponible.
                texte = reponse_courte or reponse

                fins = list(
                    re.finditer(
                        r"[.!?](?=\s|$)",
                        texte
                    )
                )

                if fins:
                    reponse = texte[
                        :fins[-1].end()
                    ].strip()
                else:
                    return (
                        "Le modèle n'a pas pu produire "
                        "une réponse complète. "
                        "Veuillez réessayer."
                    )

        reponse = nettoyer_reponse_finale(reponse)
        reponse = normaliser_citations(reponse, passages)

        if not reponse:
            return (
                "Le modèle n'a pas pu produire "
                "une réponse exploitable."
            )

        return reponse

    except requests.exceptions.Timeout:
        return (
            "Le modèle local a dépassé le délai "
            "de réponse autorisé."
        )

    except requests.exceptions.RequestException as erreur:
        return (
            "Erreur lors de la communication "
            f"avec Ollama : {erreur}"
        )

    except Exception as erreur:
        return f"Erreur pendant la génération : {erreur}"


# ============================================================
# PIPELINE RAG
# ============================================================

def executer_rag(question):
    print("\n" + "=" * 60)
    print("WEB COGNITIVE ENGINE - RAG MULTI-ASPECTS")
    print("=" * 60)

    print("\nQUESTION :", question)

    passages = rechercher_passages(question)

    print("\n--- SOURCES APRES RERANKING ---")

    for passage in passages:
        print(f"\n[Source {passage['numero']}]")
        print("Document :", passage["source"])
        print("Chunk :", passage["chunk_id"])

        numero_page = passage.get("numero_page")

        print(
            "Page PDF :",
            numero_page
            if numero_page is not None
            else "Non disponible"
        )

        print(
            "Score reranking :",
            round(passage["score_reranking"], 4)
        )

        print(
            "Aspects :",
            ", ".join(sorted(passage["aspects"]))
        )

    print("\n--- REPONSE DU MODELE ---\n")

    reponse = generer_reponse(
        question,
        passages
    )

    print(reponse)

    print("\n--- EXTRAITS DOCUMENTAIRES ---")

    for passage in passages:
        print(
            f"\n[Source {passage['numero']}] "
            f"{passage['source']}"
        )

        print("Chunk :", passage["chunk_id"])
        print("Page PDF :", passage.get("numero_page"))
        print("Extrait :", passage["texte"][:500])

    return {
        "question": question,
        "reponse": reponse,
        "sources": passages
    }


# ============================================================
# INTERACTION
# ============================================================

if __name__ == "__main__":
    while True:
        question = input(
            "\nPose ta question (ou 'quitter') : "
        ).strip()

        if question.lower() in [
            "quitter", "exit", "q"
        ]:
            print("Fin du programme.")
            break

        if not question:
            continue

        executer_rag(question)
