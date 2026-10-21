
import asyncio
import html
from pathlib import Path

import httpx
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================




API_URL = "http://127.0.0.1:8000/ask"


# ============================================================
# DESIGN BLEU NUIT
# ============================================================

st.markdown(
    """
<style>
:root {
    --fond: #080f1f;
    --sidebar: #0d192d;
    --carte: #142540;
    --bordure: #294466;
    --bleu: #60a5fa;
    --texte: #f1f5f9;
    --secondaire: #a3b4cc;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #080f1f !important;
    color: #f1f5f9 !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    max-width: 1120px;
    padding-top: 2rem;
    padding-bottom: 6rem;
}

h1, h2, h3, h4, p {
    color: #f1f5f9;
}

/* BARRE LATERALE */

[data-testid="stSidebar"] {
    background: #0d192d !important;
    border-right: 1px solid #243b5b;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

.sidebar-brand {
    padding: 12px 0 18px;
}

.sidebar-brand-name {
    font-size: 1.45rem;
    font-weight: 800;
    color: #f8fafc;
}

.sidebar-brand-name span {
    color: #60a5fa;
}

.sidebar-subtitle {
    color: #94a3b8;
    font-size: 0.83rem;
    margin-top: 6px;
}

.sidebar-section {
    color: #93c5fd;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 22px 0 12px;
}

.sidebar-panel {
    background: #142540;
    border: 1px solid #294466;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 15px;
}

.sidebar-stat {
    color: #60a5fa;
    font-size: 2rem;
    font-weight: 800;
}

.sidebar-stat-label {
    color: #a3b4cc;
    font-size: 0.85rem;
    margin-top: 6px;
}

.sidebar-format {
    color: #93c5fd;
    font-size: 0.8rem;
    margin-top: 14px;
}

.architecture-line {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 9px 0;
    border-bottom: 1px solid #263d5c;
    font-size: 0.84rem;
}

.architecture-line:last-child {
    border-bottom: none;
}

.architecture-name {
    color: #a3b4cc;
}

.architecture-value {
    color: #e2e8f0;
    font-weight: 600;
    text-align: right;
}

/* EN-TETE */

.hero {
    background: linear-gradient(
        120deg,
        #142b4c 0%,
        #10213d 55%,
        #101a30 100%
    );
    border: 1px solid #2a4b76;
    border-radius: 24px;
    padding: 32px 35px;
    margin-bottom: 28px;
}

.hero-label {
    display: inline-block;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(96, 165, 250, 0.3);
    color: #93c5fd;
    padding: 7px 13px;
    border-radius: 50px;
    font-size: 0.77rem;
    font-weight: 700;
    margin-bottom: 18px;
}

.hero-title {
    color: #f8fafc;
    font-size: clamp(1.8rem, 4vw, 2.7rem);
    font-weight: 800;
    line-height: 1.25;
    margin-bottom: 14px;
}

.hero-title span {
    color: #60a5fa;
}

.hero-description {
    color: #b6c7de;
    font-size: 0.97rem;
    line-height: 1.8;
    max-width: 750px;
}

/* ACCUEIL */

.welcome-card {
    background: #11213a;
    border: 1px solid #294466;
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 24px;
}

.welcome-title {
    color: #f1f5f9;
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.welcome-description {
    color: #a9bbd4;
    font-size: 0.92rem;
    line-height: 1.75;
}

.section-label {
    color: #dbeafe;
    font-size: 1rem;
    font-weight: 700;
    margin: 18px 0 14px;
}

/* BOUTONS */

div.stButton > button {
    background: #152943 !important;
    color: #dbeafe !important;
    border: 1px solid #31537b !important;
    border-radius: 13px !important;
    padding: 12px 15px !important;
    min-height: 60px;
    white-space: normal !important;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: #1d3b63 !important;
    border-color: #60a5fa !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] div.stButton > button {
    background: #1d4ed8 !important;
    color: white !important;
    border-color: #3b82f6 !important;
    min-height: 48px;
}

[data-testid="stSidebar"] div.stButton > button:hover {
    background: #2563eb !important;
}

/* CONVERSATION */

[data-testid="stChatMessage"] {
    background: #111f36 !important;
    border: 1px solid #263f61 !important;
    border-radius: 19px !important;
    padding: 18px 20px !important;
    margin-bottom: 17px !important;
}

[data-testid="stChatMessage"] p {
    color: #e5edf8 !important;
    line-height: 1.8;
}

[data-testid="stChatMessageAvatarUser"] {
    background: #1d4ed8 !important;
}

[data-testid="stChatMessageAvatarAssistant"] {
    background: #1e3a5f !important;
}

/* SOURCES */

[data-testid="stExpander"] {
    background: #142640 !important;
    border: 1px solid #315175 !important;
    border-radius: 15px !important;
    overflow: hidden;
    margin-top: 16px;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color: #bfdbfe !important;
    font-weight: 650;
}

.source-card {
    background: #192e4c;
    border: 1px solid #355477;
    border-radius: 15px;
    padding: 18px 20px;
    margin: 14px 0;
}

.source-card-title {
    color: #eaf2ff;
    font-size: 0.94rem;
    font-weight: 700;
    line-height: 1.6;
    overflow-wrap: anywhere;
    margin-bottom: 13px;
}

.source-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 15px;
}

.source-tag {
    display: inline-block;
    background: #25456d;
    border: 1px solid #3c638e;
    border-radius: 7px;
    color: #cfe4ff;
    padding: 5px 10px;
    font-size: 0.76rem;
    font-weight: 600;
}

.source-excerpt-label {
    color: #93c5fd;
    font-size: 0.79rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.source-excerpt {
    color: #d0deef;
    font-size: 0.89rem;
    line-height: 1.8;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    border-top: 1px solid #355477;
    padding-top: 13px;
}

/* BARRE DE QUESTION : FOND BLANC, TEXTE NOIR */

[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInputContainer"] {
    background: #080f1f !important;
}

[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 17px !important;
}

[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    caret-color: #000000 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
}

[data-testid="stChatInput"] button {
    color: #2563eb !important;
}

/* INFORMATIONS */

[data-testid="stAlert"] {
    background: #142b49 !important;
    border: 1px solid #2b507e !important;
    border-radius: 12px !important;
}

.footer-note {
    color: #8197b5;
    font-size: 0.79rem;
    line-height: 1.7;
    text-align: center;
    margin-top: 25px;
}

.sidebar-footer {
    color: #8299b7;
    font-size: 0.75rem;
    line-height: 1.7;
    margin-top: 18px;
}

hr {
    border-color: #294466 !important;
}

@media (max-width: 768px) {
    .hero {
        padding: 23px 20px;
    }

    .block-container {
        padding-top: 1rem;
    }
}
</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FONCTION POUR AFFICHER LE HTML SANS ERREUR
# ============================================================

def afficher_html(contenu):
    """
    Affiche un bloc HTML sans indentation susceptible
    d'être interprétée comme un bloc de code Markdown.
    """
    st.markdown(
        contenu.strip(),
        unsafe_allow_html=True,
    )


# ============================================================
# COMMUNICATION ASYNCHRONE AVEC FASTAPI
# ============================================================

async def interroger_api(question):
    async with httpx.AsyncClient(timeout=300.0) as client:
        reponse = await client.post(
            API_URL,
            json={"question": question},
        )

        reponse.raise_for_status()
        return reponse.json()


# ============================================================
# HISTORIQUE DES CONVERSATIONS
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# IDENTIFICATION DU FORMAT
# ============================================================

def obtenir_format(document):
    extension = Path(document).suffix.lower()

    if extension == ".pdf":
        return "PDF", "📕"

    if extension in {".html", ".htm"}:
        return "HTML", "🌐"

    if extension == ".docx":
        return "DOCX", "📝"

    return "Document", "📄"


# ============================================================
# AFFICHAGE DES SOURCES SCIENTIFIQUES
# ============================================================

def afficher_sources(sources):
    if not sources:
        st.info("Aucune source documentaire disponible.")
        return

    with st.expander(
        f"📚 Consulter les sources scientifiques ({len(sources)})"
    ):
        st.caption(
            "Ces passages ont été retrouvés par recherche "
            "sémantique et reranking. Ils constituent le "
            "contexte documentaire transmis au modèle. "
            "Tous ne sont pas nécessairement cités dans la réponse."
        )

        for source in sources:
            numero = source.get("numero", "?")

            document = str(
                source.get("document") or "Document inconnu"
            )

            extrait = str(
                source.get("extrait") or ""
            )

            chunk_id = source.get("chunk_id", "?")
            numero_page = source.get("numero_page")

            format_document, icone = obtenir_format(document)

            # Sécuriser les textes affichés dans le HTML
            numero_html = html.escape(str(numero))
            document_html = html.escape(document)
            chunk_html = html.escape(str(chunk_id))

            extrait_html = html.escape(
                extrait if extrait else "Extrait indisponible."
            )

            # Construction des étiquettes
            tags = [
                f'<span class="source-tag">'
                f'{html.escape(format_document)}'
                f'</span>'
            ]

            if (
                format_document == "PDF"
                and numero_page is not None
            ):
                page_html = html.escape(str(numero_page))

                tags.append(
                    f'<span class="source-tag">'
                    f'Page {page_html}'
                    f'</span>'
                )

            tags.append(
                f'<span class="source-tag">'
                f'Chunk {chunk_html}'
                f'</span>'
            )

            # Important :
            # HTML construit sur une seule ligne logique.
            # Cela évite les blocs blancs de code Markdown.
            carte_html = (
                '<div class="source-card">'
                '<div class="source-card-title">'
                f'{icone} Source {numero_html} — {document_html}'
                '</div>'
                '<div class="source-tags">'
                f'{"".join(tags)}'
                '</div>'
                '<div class="source-excerpt-label">'
                'EXTRAIT SCIENTIFIQUE'
                '</div>'
                '<div class="source-excerpt">'
                f'{extrait_html}'
                '</div>'
                '</div>'
            )

            afficher_html(carte_html)


# ============================================================
# BARRE LATÉRALE
# ============================================================

with st.sidebar:

    afficher_html(
        '<div class="sidebar-brand">'
        '<div class="sidebar-brand-name">'
        '🧠 Web<span>Cognitive</span>'
        '</div>'
        '<div class="sidebar-subtitle">'
        'Scientific Knowledge Assistant'
        '</div>'
        '</div>'
    )

    afficher_html(
        '<div class="sidebar-section">'
        'Corpus scientifique'
        '</div>'
    )

    afficher_html(
        '<div class="sidebar-panel">'
        '<div class="sidebar-stat">35</div>'
        '<div class="sidebar-stat-label">'
        'Documents scientifiques indexés'
        '</div>'
        '<div class="sidebar-format">'
        'PDF · HTML · DOCX'
        '</div>'
        '</div>'
    )

    afficher_html(
        '<div class="sidebar-section">'
        'Architecture RAG'
        '</div>'
    )

    architecture = [
        ("Base vectorielle", "ChromaDB"),
        ("Embeddings", "MiniLM"),
        ("Reranking", "Cross-Encoder"),
        ("Modèle LLM", "Qwen 2.5"),
        ("Exécution locale", "Ollama"),
        ("API", "FastAPI"),
    ]

    lignes_architecture = ""

    for nom, valeur in architecture:
        lignes_architecture += (
            '<div class="architecture-line">'
            '<span class="architecture-name">'
            f'{html.escape(nom)}'
            '</span>'
            '<span class="architecture-value">'
            f'{html.escape(valeur)}'
            '</span>'
            '</div>'
        )

    afficher_html(
        '<div class="sidebar-panel">'
        f'{lignes_architecture}'
        '</div>'
    )

    afficher_html(
        '<div class="sidebar-section">'
        'Conversation'
        '</div>'
    )

    if st.button(
        "✦ Nouvelle conversation",
        use_container_width=True,
        key="nouvelle_conversation",
    ):
        st.session_state.messages = []
        st.rerun()

    afficher_html(
        '<div class="sidebar-footer">'
        'WebCognitive Engine'
        '<br>'
        'Projet universitaire · RAG local'
        '</div>'
    )


# ============================================================
# EN-TÊTE PRINCIPAL
# ============================================================

afficher_html(
    '<div class="hero">'
    '<div class="hero-label">'
    '✦ ASSISTANT SCIENTIFIQUE · RAG LOCAL'
    '</div>'
    '<div class="hero-title">'
    'Explorez la médecine<br>'
    '<span>de demain.</span>'
    '</div>'
    '<div class="hero-description">'
    'Découvrez comment les jumeaux numériques '
    'transforment le diagnostic, le suivi et les '
    'traitements médicaux. Interrogez un corpus '
    'scientifique grâce à une intelligence artificielle '
    'locale et consultez les sources documentaires '
    'de chaque réponse.'
    '</div>'
    '</div>'
)


# ============================================================
# QUESTIONS SUGGÉRÉES
# ============================================================

question_suggeree = None

if not st.session_state.messages:

    afficher_html(
        '<div class="welcome-card">'
        '<div class="welcome-title">'
        '✨ Bienvenue dans WebCognitive Engine'
        '</div>'
        '<div class="welcome-description">'
        'Posez une question sur les jumeaux numériques '
        'en médecine. L’assistant recherche les passages '
        'pertinents dans le corpus, génère une réponse '
        'et affiche les références scientifiques utilisées '
        'comme contexte.'
        '</div>'
        '</div>'
    )

    afficher_html(
        '<div class="section-label">'
        '💡 Pour commencer, essayez une question'
        '</div>'
    )

    exemples = [
        "Qu'est-ce qu'un jumeau numérique en médecine ?",
        "Comment améliorer la médecine personnalisée ?",
        "Quelles sont les limites des jumeaux numériques ?",
    ]

    colonnes = st.columns(3, gap="medium")

    for index, (colonne, exemple) in enumerate(
        zip(colonnes, exemples)
    ):
        with colonne:
            if st.button(
                exemple,
                use_container_width=True,
                key=f"exemple_{index}",
            ):
                question_suggeree = exemple


# ============================================================
# AFFICHAGE DE L'HISTORIQUE
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["contenu"])

        if message["role"] == "assistant":
            afficher_sources(
                message.get("sources", [])
            )


# ============================================================
# BARRE DE SAISIE
# ============================================================

question_saisie = st.chat_input(
    "Posez votre question sur les jumeaux numériques..."
)

question = question_suggeree or question_saisie


# ============================================================
# TRAITEMENT D'UNE NOUVELLE QUESTION
# ============================================================

if question:

    st.session_state.messages.append({
        "role": "user",
        "contenu": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner(
            "Recherche des documents et génération "
            "de la réponse..."
        ):

            try:
                resultat = asyncio.run(
                    interroger_api(question)
                )

                reponse = resultat.get(
                    "reponse",
                    "Aucune réponse générée.",
                )

                sources = resultat.get(
                    "sources",
                    [],
                )

                st.markdown(reponse)

                afficher_sources(sources)

            except httpx.ConnectError:

                reponse = (
                    "Impossible de joindre l'API FastAPI. "
                    "Vérifiez que le serveur est démarré "
                    "sur http://127.0.0.1:8000."
                )

                sources = []
                st.error(reponse)

            except httpx.HTTPStatusError as erreur:

                reponse = (
                    f"Erreur de l'API : "
                    f"{erreur.response.status_code}"
                )

                sources = []
                st.error(reponse)

            except httpx.TimeoutException:

                reponse = (
                    "Le traitement a dépassé le délai autorisé. "
                    "Réessayez dans quelques instants."
                )

                sources = []
                st.error(reponse)

            except Exception as erreur:

                reponse = (
                    f"Erreur inattendue : {erreur}"
                )

                sources = []
                st.error(reponse)

    st.session_state.messages.append({
        "role": "assistant",
        "contenu": reponse,
        "sources": sources,
    })


# ============================================================
# PIED DE PAGE
# ============================================================

afficher_html(
    '<div class="footer-note">'
    'WebCognitive Engine · Intelligence artificielle locale'
    '<br>'
    'Les réponses sont générées automatiquement à partir '
    'd’un corpus scientifique. Vérifiez les sources '
    'avant toute utilisation médicale.'
    '</div>'
)
