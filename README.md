
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

### Statistiques du corpus indexé

| Indicateur | Valeur |
|---|---:|
| Documents scientifiques | 35 |
| Chunks indexés | 6 582 |
| Chunks par document en moyenne | 188,1 |
| Mots par chunk en moyenne | 72,9 |

### Formats documentaires

| Format | Proportion |
|---|---:|
| PDF | 80 % |
| HTML | 14,3 % |
| DOCX | 5,7 % |

Les statistiques sont calculées à partir des données indexées dans ChromaDB.

---

## 4. Architecture technique

L'application repose sur une architecture modulaire.

```text
Documents scientifiques
        |
        v
Extraction et nettoyage
        |
        v
Segmentation en chunks
        |
        v
Vectorisation des textes
        |
        v
Base vectorielle ChromaDB
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
| `parser.py` | Extraction des contenus documentaires |
| `chunking.py` | Segmentation des documents |
| `indexation.py` | Vectorisation et indexation |
| `database.py` | Gestion des données |
| `recherche.py` | Recherche documentaire |
| `rag.py` | Pipeline RAG et génération |
| `api.py` | API REST FastAPI |
| `interface.py` | Assistant scientifique Streamlit |
| `analyse_corpus.py` | Analyse statistique du corpus |
| `dashboard.py` | Visualisations du corpus |
| `app.py` | Application principale et navigation |
| `evaluation_rag.py` | Évaluation du système RAG |

Les répertoires du projet comprennent également le corpus scientifique, les données nettoyées et les données vectorisées.

---

## 6. Installation et lancement en local

### Prérequis

- Python
- Ollama
- Les dépendances Python nécessaires au projet
- Le modèle local `qwen2.5:7b`
- La base ChromaDB du projet

### Étape 1 — Ouvrir le projet

Dans un terminal PowerShell :

```powershell
cd C:\Users\celia\Desktop\WebCognitive
```

### Étape 2 — Créer un environnement virtuel

Lors de la première installation :

```powershell
python -m venv .venv
```

Activer l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installer les dépendances du projet dans cet environnement.

### Étape 3 — Préparer Ollama

Vérifier qu'Ollama est installé et disponible.

Télécharger le modèle si nécessaire :

```powershell
ollama pull qwen2.5:7b
```

Démarrer Ollama si son service n'est pas déjà actif :

```powershell
ollama serve
```

### Étape 4 — Démarrer FastAPI

Ouvrir un terminal dans le dossier `src` :

```powershell
cd C:\Users\celia\Desktop\WebCognitive\src
```

Exécuter :

```powershell
python -m uvicorn api:app --reload --port 8000
```

L'API est accessible à l'adresse :

http://127.0.0.1:8000

Sa documentation interactive est disponible à :

http://127.0.0.1:8000/docs

### Étape 5 — Démarrer Streamlit

Ouvrir un deuxième terminal, sans fermer FastAPI.

```powershell
cd C:\Users\celia\Desktop\WebCognitive\src
```

Exécuter :

```powershell
python -m streamlit run app.py
```

L'interface est accessible à l'adresse :

http://localhost:8501

### Étape 6 — Utiliser l'application

Dans la barre latérale, sélectionner :

- **Assistant scientifique** pour interroger les documents.
- **Analyse du corpus** pour consulter les statistiques et graphiques.

Pour obtenir une réponse scientifique, saisir une question et attendre la génération du texte.

Les sources documentaires sont consultables sous la réponse.

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

Ces vérifications confirment le fonctionnement des composants testés. Elles ne constituent pas, à elles seules, une mesure exhaustive de la précision scientifique des réponses.

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

---

## 11. Conclusion

WebCognitive Engine illustre l'intégration de plusieurs technologies d'intelligence artificielle et de développement web dans une application documentaire complète.

Le projet combine l'extraction de documents scientifiques, la recherche sémantique, la génération de réponses par un modèle local, une API REST et une interface interactive.

L'ajout d'un module de visualisation permet également de mieux comprendre la composition du corpus et sa segmentation.

Cette réalisation met en évidence l'intérêt des systèmes RAG pour l'exploration de connaissances scientifiques, tout en soulignant l'importance de la traçabilité des sources et de la validation des réponses générées.
