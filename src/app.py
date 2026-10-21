
import streamlit as st

# ============================================================
# WEBCOGNITIVE ENGINE - APPLICATION PRINCIPALE
# ============================================================

st.set_page_config(
    page_title="WebCognitive Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# DESIGN GLOBAL
# ============================================================

st.markdown(
    """
    <style>

    /* Fond principal */
    .stApp {
        background-color: #080f1f;
        color: #e2e8f0;
    }

    /* Barre latérale */
    [data-testid="stSidebar"] {
        background-color: #0d192d !important;
    }

    [data-testid="stSidebar"] > div {
        background-color: #0d192d !important;
    }

    /* Textes de la navigation */
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #dbeafe !important;
    }

    /* Page sélectionnée */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #243b5b !important;
        border-radius: 9px;
    }

    /* Titres */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# NAVIGATION
# ============================================================

assistant = st.Page(
    "interface.py",
    title="Assistant scientifique",
    icon="🧠",
    default=True
)

analyse = st.Page(
    "dashboard.py",
    title="Analyse du corpus",
    icon="📊"
)

navigation = st.navigation(
    {
        "WEBCOGNITIVE ENGINE": [
            assistant,
            analyse
        ]
    },
    position="sidebar"
)

navigation.run()
