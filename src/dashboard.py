
from pathlib import Path
from collections import Counter
import re

import chromadb
import plotly.express as px
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

# IMPORTANT :
# st.set_page_config() est dans app.py.
# Il ne faut pas le répéter ici.

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
# DESIGN BLEU NUIT
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #080f1f;
        color: #e2e8f0;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp p {
        color: #e2e8f0;
    }

    /* EN-TÊTE */

    .dashboard-intro {
        background: linear-gradient(
            120deg,
            #142b4c,
            #101a30
        );
        border: 1px solid #2a4b76;
        border-radius: 22px;
        padding: 30px 35px;
        margin-bottom: 28px;
    }

    .dashboard-title {
        font-size: 2rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.3;
    }

    .dashboard-description {
        color: #b6c7de;
        margin-top: 15px;
        font-size: 1rem;
        line-height: 1.7;
    }

    /* INDICATEURS */

    [data-testid="stMetric"] {
        background: #142540;
        border: 1px solid #294466;
        border-radius: 16px;
        padding: 20px;
    }

    [data-testid="stMetricLabel"] p {
        color: #cbd5e1 !important;
    }

    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
    }

    /* ENCADRÉS */

    [data-testid="stAlert"] {
        background-color: #172b49 !important;
        border: 1px solid #355477 !important;
        border-radius: 14px;
    }

    [data-testid="stAlert"] p {
        color: #dbeafe !important;
    }

    /* TEXTE SECONDAIRE */

    [data-testid="stCaptionContainer"] p {
        color: #a3b4cc !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


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

    return len(
        re.findall(r"\b\w+\b", texte)
    )


def contient_expression(texte, expression):

    motif = (
        r"(?<!\w)"
        + re.escape(expression.lower())
        + r"(?!\w)"
    )

    return re.search(motif, texte) is not None


# ============================================================
# CHARGEMENT ET ANALYSE DU CORPUS
# ============================================================

@st.cache_data(
    show_spinner="Analyse du corpus scientifique..."
)
def charger_statistiques():

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

    documents = set()
    chunks_par_document = Counter()
    tailles = []

    themes_chunks = Counter()

    themes_documents = {
        theme: set()
        for theme in MOTS_CLES
    }

    for texte, metadata in zip(
        textes,
        metadonnees
    ):

        metadata = metadata or {}
        texte = texte or ""

        source = str(
            metadata.get(
                "source",
                "Source inconnue"
            )
        )

        documents.add(source)

        chunks_par_document[source] += 1

        tailles.append(
            compter_mots(texte)
        )

        texte_min = texte.lower()

        for theme, expressions in MOTS_CLES.items():

            if any(
                contient_expression(
                    texte_min,
                    expression
                )
                for expression in expressions
            ):

                themes_chunks[theme] += 1
                themes_documents[theme].add(source)

    formats = Counter(
        identifier_format(document)
        for document in documents
    )

    return {
        "nombre_documents": len(documents),
        "nombre_chunks": len(textes),
        "formats": dict(formats),
        "tailles": tailles,
        "chunks_par_document": dict(
            chunks_par_document
        ),
        "themes_chunks": dict(
            themes_chunks
        ),
        "themes_documents": {
            theme: len(sources)
            for theme, sources in themes_documents.items()
        },
    }


# ============================================================
# AMÉLIORATION DES GRAPHIQUES
# ============================================================

def ameliorer_graphique(fig):

    fig.update_layout(
        template="plotly_dark",

        font=dict(
            color="#e2e8f0",
            size=13
        ),

        title_font=dict(
            color="#f8fafc",
            size=18
        ),

        legend=dict(
            font=dict(
                color="#e2e8f0"
            ),
            title_font=dict(
                color="#e2e8f0"
            ),
        ),

        paper_bgcolor="#142540",
        plot_bgcolor="#142540",

        margin=dict(
            l=35,
            r=30,
            t=75,
            b=50
        ),

        hoverlabel=dict(
            bgcolor="#25456d",
            font_color="#ffffff"
        ),
    )

    fig.update_xaxes(
        tickfont=dict(
            color="#cbd5e1"
        ),
        title_font=dict(
            color="#cbd5e1"
        ),
        gridcolor="#355477",
        zerolinecolor="#355477"
    )

    fig.update_yaxes(
        tickfont=dict(
            color="#cbd5e1"
        ),
        title_font=dict(
            color="#cbd5e1"
        ),
        gridcolor="#355477",
        zerolinecolor="#355477"
    )

    return fig


# ============================================================
# EN-TÊTE
# ============================================================

st.markdown(
    '<div class="dashboard-intro">'
    '<div class="dashboard-title">'
    '📊 Analyse du corpus scientifique'
    '</div>'
    '<div class="dashboard-description">'
    'Explorez les caractéristiques documentaires, '
    'la segmentation textuelle et les thématiques '
    'scientifiques des jumeaux numériques en médecine.'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# CHARGEMENT DES STATISTIQUES
# ============================================================

try:

    stats = charger_statistiques()

except Exception as erreur:

    st.error(
        "Impossible de charger les statistiques : "
        f"{erreur}"
    )

    st.stop()


# ============================================================
# INDICATEURS GÉNÉRAUX
# ============================================================

nombre_documents = stats["nombre_documents"]
nombre_chunks = stats["nombre_chunks"]
tailles = stats["tailles"]

moyenne_chunks = (
    nombre_chunks / nombre_documents
    if nombre_documents
    else 0
)

moyenne_mots = (
    sum(tailles) / len(tailles)
    if tailles
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "📚 Documents",
    nombre_documents
)

col2.metric(
    "🧩 Chunks",
    f"{nombre_chunks:,}".replace(",", " ")
)

col3.metric(
    "📄 Chunks / document",
    f"{moyenne_chunks:.1f}"
)

col4.metric(
    "✍️ Mots / chunk",
    f"{moyenne_mots:.1f}"
)


# ============================================================
# GRAPHIQUES 1 ET 2
# ============================================================

st.markdown("## Vue d'ensemble du corpus")

col_gauche, col_droite = st.columns(2)

# ------------------------------------------------------------
# GRAPHIQUE 1 : FORMATS
# ------------------------------------------------------------

with col_gauche:

    formats = stats["formats"]

    fig_formats = px.pie(
        names=list(formats.keys()),
        values=list(formats.values()),
        hole=0.55,
        title="Répartition des documents par format",
        color_discrete_sequence=[
            "#60a5fa",
            "#2563eb",
            "#93c5fd",
            "#38bdf8"
        ]
    )

    fig_formats.update_traces(
        textinfo="percent",
        textfont=dict(
            color="#ffffff",
            size=14
        ),
        hovertemplate=(
            "%{label}<br>"
            "%{value} documents<br>"
            "%{percent}<extra></extra>"
        )
    )

    fig_formats.update_layout(
        legend_title_text="Format"
    )

    st.plotly_chart(
        ameliorer_graphique(fig_formats),
        use_container_width=True
    )


# ------------------------------------------------------------
# GRAPHIQUE 2 : THÉMATIQUES
# ------------------------------------------------------------

with col_droite:

    themes = stats["themes_chunks"]

    themes_tries = sorted(
        themes.items(),
        key=lambda element: element[1],
        reverse=True
    )

    fig_themes = px.bar(
        x=[
            nom
            for nom, nombre in themes_tries
        ],
        y=[
            nombre
            for nom, nombre in themes_tries
        ],
        title="Présence des thématiques dans les chunks",
        labels={
            "x": "Thématique",
            "y": "Nombre de chunks"
        },
        color=[
            nombre
            for nom, nombre in themes_tries
        ],
        color_continuous_scale="Blues"
    )

    fig_themes.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_tickangle=-40
    )

    fig_themes.update_traces(
        hovertemplate=(
            "%{x}<br>"
            "%{y} chunks"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        ameliorer_graphique(fig_themes),
        use_container_width=True
    )


# ============================================================
# GRAPHIQUES 3 ET 4
# ============================================================

st.markdown(
    "## Analyse de la segmentation documentaire"
)

col_gauche, col_droite = st.columns(2)

# ------------------------------------------------------------
# GRAPHIQUE 3 : TAILLE DES CHUNKS
# ------------------------------------------------------------

with col_gauche:

    fig_tailles = px.histogram(
        x=tailles,
        nbins=25,
        title="Distribution de la taille des chunks",
        labels={
            "x": "Nombre de mots par chunk",
            "y": "Nombre de chunks"
        },
        color_discrete_sequence=[
            "#60a5fa"
        ]
    )

    fig_tailles.update_traces(
        hovertemplate=(
            "Taille : %{x} mots<br>"
            "Chunks : %{y}"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        ameliorer_graphique(fig_tailles),
        use_container_width=True
    )


# ------------------------------------------------------------
# GRAPHIQUE 4 : DOCUMENTS LES PLUS VOLUMINEUX
# ------------------------------------------------------------

with col_droite:

    top_documents = sorted(
        stats["chunks_par_document"].items(),
        key=lambda element: element[1],
        reverse=True
    )[:10]

    fig_documents = px.bar(
        x=[
            nombre
            for nom, nombre in top_documents
        ],
        y=[
            nom
            for nom, nombre in top_documents
        ],
        orientation="h",
        title="Top 10 des documents par nombre de chunks",
        labels={
            "x": "Nombre de chunks",
            "y": "Document"
        },
        color_discrete_sequence=[
            "#3b82f6"
        ]
    )

    fig_documents.update_layout(
        yaxis=dict(
            categoryorder="total ascending"
        ),
         xaxis=dict(
              tickangle=0,
              tickmode="array",
              tickvals=[0, 200, 400],
              ticktext=["0", "200", "400"],
             automargin=True,
             showgrid=True
        ),
        margin=dict(
            l=20,
            r=25,
            t=75,
            b=65
        )
    )

    fig_documents.update_traces(
        hovertemplate=(
            "%{y}<br>"
            "%{x} chunks"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        ameliorer_graphique(fig_documents),
        use_container_width=True
    )


# ============================================================
# INTERPRÉTATION DES RÉSULTATS
# ============================================================

st.markdown("## Interprétation des résultats")

if stats["themes_chunks"]:

    theme_principal = max(
        stats["themes_chunks"],
        key=stats["themes_chunks"].get
    )

    nombre_theme = stats["themes_chunks"][
        theme_principal
    ]

    st.markdown(
        f"**Thématique la plus représentée :** "
        f"{theme_principal} "
        f"({nombre_theme} chunks)."
    )

if tailles:

    st.markdown(
        f"**Taille moyenne des chunks :** "
        f"{moyenne_mots:.1f} mots."
    )

st.info(
    "Les analyses sont calculées à partir des documents "
    "indexés dans ChromaDB. Une thématique est comptée "
    "une fois par chunk lorsqu'au moins un de ses "
    "mots-clés apparaît. Plusieurs thématiques peuvent "
    "être présentes dans un même chunk."
)

st.caption(
    "WebCognitive Engine · Étape 7/8 · "
    "Dataviz et analyse exploratoire"
)
