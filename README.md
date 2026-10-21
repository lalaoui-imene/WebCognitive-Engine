
# 🧠 WebCognitive Engine

## 1. Présentation du projet

WebCognitive Engine est une application web intelligente permettant d'interroger un corpus de documents scientifiques à l'aide d'un système de génération augmentée par récupération (RAG — Retrieval-Augmented Generation).

Le projet a été développé dans le cadre du Master 2 Technologies de l'Hypermédia à l'Université Paris 8.

### Thématique

**Les jumeaux numériques en médecine : applications, apports et limites pour la médecine personnalisée.**

### Problématique

Comment les jumeaux numériques peuvent-ils contribuer à la personnalisation du diagnostic, du suivi et des traitements médicaux, et quelles sont les limites actuelles de leur utilisation en pratique clinique ?

L'objectif est de fournir des réponses en français, fondées sur des publications scientifiques, tout en permettant de consulter les sources documentaires utilisées.

---

## 2. Fonctionnalités principales

L'application propose deux espaces complémentaires.

### Assistant scientifique

- Saisie de questions en langage naturel.
- Recherche sémantique dans le corpus scientifique.
- Reclassement des passages pertinents par reranking.
- Génération de réponses en français avec un modèle de langage local.
- Affichage des références documentaires.
- Identification du fichier source et du numéro de page pour les PDF.
- Consultation des extraits scientifiques retrouvés.

### Analyse du corpus

- Présentation des indicateurs documentaires.
- Répartition des documents par format.
- Analyse des principales thématiques scientifiques.
- Visualisation de la distribution des tailles des chunks.
- Identification des documents possédant le plus de chunks.
- Interprétation des statistiques du corpus.

---

## 3. Corpus documentaire

Le corpus porte sur les applications médicales des jumeaux numériques, notamment la médecine personnalisée, le diagnostic, le suivi des patients, les traitements, l'oncologie, la cardiologie et les limites techniques et éthiques.

### Statistiques du corpus reconstruit

| Indicateur | Valeur |
|---|---:|
| Documents scientifiques | 34 |
| Chunks indexés | 6 456 |
| Chunks par document en moyenne | 189,9 |

### Formats documentaires

| Format | Proportion |
|---|---:|
| PDF | 82,4 % |
| HTML | 11,8 % |
| DOCX | 5,9 % |

Ces statistiques correspondent à la reconstruction indépendante du corpus de 34 documents.

Les résultats détaillés de cette reconstruction sont présentés dans la section 8.

Les statistiques peuvent varier selon les documents disponibles et les paramètres d'indexation.

---

## 4. Architecture technique

L'application repose sur une architecture modulaire.

```text
Documents scientifiques
        |
        v
Extraction et nettoyage (parser.py)
        |
        v
Segmentation en chunks (chunking.py)
        |
        v
Vectorisation des textes (chunking.py)
        |
        v
Base vectorielle ChromaDB (indexation.py)
        |
        v
Recherche sémantique
        |
        v
Reranking des passages
        |
        v
Construction du contexte RAG
        |
        v
Modèle local Ollama
        |
        v
API REST FastAPI
        |
        v
Interface web Streamlit
        |
        +---- Assistant scientifique
        |
        +---- Analyse du corpus
```

### Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Développement de l'application |
| ChromaDB | Stockage et recherche vectorielle |
| Sentence Transformers | Génération des embeddings |
| all-MiniLM-L6-v2 | Modèle d'embedding |
| Cross-Encoder MiniLM | Reranking des passages |
| Ollama | Exécution locale du modèle de langage |
| Qwen2.5:7b | Génération des réponses |
| FastAPI | API REST |
| Streamlit | Interface web |
| Plotly | Visualisations interactives |

Le système fonctionne localement, sans nécessiter une API commerciale de génération de texte.

---

## 5. Organisation du code

Les principaux fichiers Python sont regroupés dans le dossier `src`.

| Fichier | Rôle |
|---|---|
| `parser.py` | Extraction et nettoyage des documents scientifiques |
| `chunking.py` | Segmentation des documents et génération des embeddings |
| `indexation.py` | Indexation des vecteurs dans ChromaDB |
| `database.py` | Gestion des données |
| `recherche.py` | Recherche documentaire |
| `rag.py` | Pipeline RAG et génération |
| `api.py` | API REST FastAPI |
| `interface.py` | Assistant scientifique Streamlit |
| `analyse_corpus.py` | Analyse statistique du corpus |
| `dashboard.py` | Visualisations du corpus |
| `app.py` | Application principale et navigation |
| `evaluation_rag.py` | Évaluation du système RAG |

### Répertoires de données

| Répertoire | Contenu |
|---|---|
| `corpus_complet/` | Documents scientifiques d'origine |
| `data_clean/` | Documents extraits et nettoyés au format JSON |
| `data_vectors_pages/` | Chunks et embeddings générés |
| `chroma_db/` | Base vectorielle persistante ChromaDB |
| `evaluation/` | Fichiers d'évaluation du système |

Les répertoires de données locales ne sont pas tous publiés sur GitHub. Ils peuvent être créés lors de l'exécution du pipeline.

---

## 6. Installation et lancement en local

### Prérequis

- Python et Git installés.
- Ollama installé pour exécuter le modèle local `qwen2.5:7b`.
- Un corpus documentaire disponible localement pour construire la base ChromaDB.

**Important :** les 34 documents scientifiques sont disponibles dans le dossier `corpus_complet/` du dépôt GitHub. La base vectorielle `chroma_db/` et les données intermédiaires doivent être reconstruites localement en suivant les étapes ci-dessous.

### Étape 1 — Récupérer le projet

Dans un terminal PowerShell, depuis le dossier où vous souhaitez installer le projet :

```powershell
git clone https://github.com/lalaoui-imene/WebCognitive-Engine.git
cd WebCognitive-Engine
```

### Étape 2 — Créer un environnement virtuel et installer les dépendances

À la racine du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Pour vérifier les dépendances installées :

```powershell
python -m pip check
```

Si l'activation PowerShell est bloquée par la politique d'exécution, il est également possible d'appeler directement `.venv\Scripts\python.exe` pour les commandes Python.

### Étape 3 — Préparer Ollama

Télécharger le modèle local :

```powershell
ollama pull qwen2.5:7b
```

Vérifier qu'Ollama est lancé. Si son service n'est pas déjà actif, démarrer dans un terminal séparé :

```powershell
ollama serve
```

### Étape 4 — Préparer le corpus et reconstruire ChromaDB

Le dépôt contient les 34 documents scientifiques dans le dossier corpus_complet/. La base vectorielle est reconstruite localement.

Pour utiliser le système RAG, il est nécessaire de disposer de documents scientifiques dont l'utilisation est autorisée.

**1. Préparer les documents**

Les 34 documents scientifiques sont déjà présents dans le dossier `corpus_complet/`. Aucune copie supplémentaire n'est nécessaire.

**2. Extraire et nettoyer les documents**

Depuis la racine du projet, avec l'environnement virtuel activé :

```powershell
python src/parser.py
```

Cette commande :

- Extrait le texte des documents scientifiques.
- Nettoie les espaces et les retours à la ligne.
- Conserve les numéros de page des PDF.
- Génère les fichiers JSON dans le dossier `data_clean/`.

**3. Générer les chunks et les embeddings**

```powershell
python src/chunking.py
```

Cette commande :

- Découpe les textes en chunks de 500 caractères.
- Applique un chevauchement de 100 caractères.
- Génère les embeddings avec `all-MiniLM-L6-v2`.
- Conserve les métadonnées documentaires et les numéros de page disponibles.
- Enregistre les résultats dans `data_vectors_pages/`.

Chaque embedding possède une dimension de 384.

**4. Construire la base vectorielle ChromaDB**

```powershell
python src/indexation.py
```

Cette commande crée ou récupère la collection :

`webcognitive_documents_pages`

Les chunks vectorisés sont indexés dans le dossier `chroma_db/`, avec leurs textes et métadonnées.

**5. Vérifier la reconstruction**

Le script affiche un bilan comprenant :

- Le nombre de documents trouvés.
- Le nombre de chunks traités.
- Le nombre d'erreurs.
- Le nombre de vecteurs présents dans ChromaDB.

**Validation réalisée :**

Le pipeline complet a été exécuté avec succès dans un dossier de reconstruction indépendant, sans utiliser la base ChromaDB initiale.

Résultats obtenus :

| Indicateur | Résultat |
|---|---:|
| Documents traités | 34 |
| Fichiers JSON nettoyés | 34 |
| Chunks générés | 6 456 |
| Chunks indexés | 6 456 |
| Erreurs de vectorisation | 0 |
| Erreurs d'indexation | 0 |
| Chunks avec numéro de page | 5 815 |

Cette validation confirme que la base vectorielle peut être reconstruite à partir des documents scientifiques disponibles.

Les statistiques de la section 3 correspondent à la reconstruction indépendante réalisée à partir des 34 documents scientifiques.

### Étape 5 — Démarrer FastAPI

Depuis la racine du projet, dans un terminal où l'environnement virtuel est activé :

```powershell

python -m uvicorn src.api:app --reload --port 8000
```

L'API est accessible à l'adresse :

http://127.0.0.1:8000

Sa documentation interactive est disponible à :

http://127.0.0.1:8000/docs

### Étape 6 — Démarrer Streamlit

Ouvrir **un deuxième terminal**, sans arrêter FastAPI.

Depuis la racine du projet, activer l'environnement virtuel puis lancer :

```powershell
.\.venv\Scripts\Activate.ps1

python -m streamlit run src/app.py
```

L'interface est accessible à l'adresse :

http://localhost:8501

### Étape 7 — Utiliser l'application

Dans la barre latérale, sélectionner :

- **Assistant scientifique** pour poser des questions au corpus et consulter les citations.
- **Analyse du corpus** pour consulter les statistiques et graphiques.

Pour interroger les documents, la base ChromaDB et le service Ollama doivent être disponibles.

---

## 7. Exemple d'utilisation

### Question

Comment les jumeaux numériques contribuent-ils à la médecine personnalisée ?

### Fonctionnement

1. L'utilisateur saisit sa question.
2. La question est transmise à FastAPI.
3. Le moteur RAG recherche les passages pertinents dans ChromaDB.
4. Les passages sont reclassés par un modèle de reranking.
5. Les meilleurs passages sont transmis au modèle Qwen2.5.
6. Le modèle génère une réponse en français.
7. Streamlit affiche la réponse et les références documentaires.

Les références peuvent inclure le nom du document, le format, le numéro de page pour les PDF et l'identifiant du chunk.

---

## 8. Validation et tests

### Tests fonctionnels

Des tests manuels ont été réalisés sur les principales fonctionnalités de l'application.

| Fonctionnalité | Résultat observé |
|---|---|
| Clonage du dépôt GitHub | Réussi |
| Installation des dépendances | Réussie |
| Vérification des dépendances | Réussie |
| Vérification syntaxique des scripts | Réussie |
| Démarrage FastAPI | Fonctionnel |
| Démarrage Streamlit | Fonctionnel |
| Communication Streamlit / FastAPI | Fonctionnelle |
| Recherche documentaire RAG | Fonctionnelle sur les questions testées |
| Génération de réponses | Fonctionnelle |
| Affichage des citations | Fonctionnel |
| Affichage des sources PDF et HTML | Fonctionnel |
| Affichage des numéros de page PDF | Fonctionnel |
| Affichage des statistiques du corpus | Fonctionnel |
| Affichage des graphiques | Fonctionnel |

Ces tests ont été réalisés à partir d'une copie du dépôt GitHub et d'une base ChromaDB locale contenant les documents initialement indexés.

### Validation de la reconstruction de la base documentaire

Un test complémentaire a été réalisé dans un dossier indépendant afin de vérifier que la base ChromaDB pouvait être reconstruite sans réutiliser la base vectorielle existante.

Les étapes suivantes ont été exécutées :

1. Récupération des 34 documents scientifiques depuis le dépôt GitHub.
2. Exécution de `parser.py` pour extraire et nettoyer les documents.
3. Exécution de `chunking.py` pour générer les chunks et les embeddings.
4. Exécution de `indexation.py` pour créer une nouvelle base ChromaDB.
5. Vérification du nombre de vecteurs et des métadonnées de pagination.

**Résultat : 34 documents traités, 6 456 vecteurs indexés et aucune erreur signalée.**

La vérification des métadonnées a confirmé la présence d'un numéro de page pour 5 815 chunks.

Cette expérience valide le fonctionnement de la chaîne de préparation et d'indexation sur le corpus testé.

Elle ne constitue pas à elle seule une validation complète de la précision scientifique des réponses générées.

### Points à surveiller

- Pertinence des passages sélectionnés.
- Correspondance entre les affirmations générées et leurs citations.
- Temps de réponse du modèle local.
- Qualité des documents et des textes extraits.
- Risques de réponses inexactes ou insuffisamment justifiées.

---

## 9. Limites du projet

Le système présente plusieurs limites :

- La qualité des réponses dépend du contenu et de la couverture du corpus scientifique.
- Le modèle peut produire des affirmations incorrectes malgré la présence de sources.
- Les temps de génération dépendent des ressources matérielles disponibles.
- Certains passages peuvent être incomplets à cause de la segmentation documentaire.
- La recherche sémantique ne garantit pas que tous les documents pertinents seront retrouvés.
- Les 34 documents scientifiques sont disponibles dans corpus_complet/.
- Une nouvelle installation nécessite la reconstruction de la base vectorielle à partir du corpus fourni.

Les réponses générées constituent une aide à l'exploration documentaire et ne doivent pas être considérées comme des recommandations médicales.

---

## 10. Perspectives d'amélioration

Plusieurs évolutions peuvent être envisagées :

- Élargissement du corpus scientifique.
- Évaluation systématique des réponses sur un jeu de questions de référence.
- Vérification plus stricte de la correspondance entre citations et passages.
- Optimisation des performances du pipeline RAG.
- Amélioration de la navigation entre les réponses et les documents originaux.
- Enrichissement des visualisations statistiques.
- Automatisation de la préparation du corpus et de la reconstruction de ChromaDB.

---

## 11. Conclusion

WebCognitive Engine illustre l'intégration de plusieurs technologies d'intelligence artificielle et de développement web dans une application documentaire complète.

Le projet combine l'extraction et le nettoyage de documents scientifiques, leur segmentation, la génération d'embeddings, la recherche sémantique, le reranking, la génération de réponses par un modèle local, une API REST et une interface interactive.

L'ajout d'un module de visualisation permet également de mieux comprendre la composition du corpus et sa segmentation.

Les tests fonctionnels réalisés, ainsi que la reconstruction indépendante de la base ChromaDB à partir de 34 documents et de 6 456 chunks, ont permis de vérifier le fonctionnement des principales composantes techniques du projet.

Cette réalisation met en évidence l'intérêt des systèmes RAG pour l'exploration de connaissances scientifiques, tout en soulignant l'importance de la traçabilité des sources, de la reproductibilité des traitements et de la validation des réponses générées.

---


## 12. Reproduction du projet depuis GitHub

Les 34 documents scientifiques sont déjà disponibles dans le dossier corpus_complet/ (28 PDF, 4 HTML et 2 DOCX).

Après installation des dépendances, exécuter depuis la racine du projet :

- python src/parser.py
- python src/chunking.py
- python src/indexation.py

Ces commandes reconstruisent la base ChromaDB. La reconstruction indépendante a produit 6 456 vecteurs sans erreur.

Pour lancer Ollama, FastAPI et Streamlit, suivre les instructions de la section 6.

Aucune copie manuelle des documents n'est nécessaire.







