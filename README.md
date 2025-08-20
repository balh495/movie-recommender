# Movie Recommender

Système de recommendation de film basé sur les métadonnées et le traitement du langage naturel.

## Description du Projet

Ce projet propose un système de recommandation de films qui utilise des techniques avancées de traitement du langage naturel via les embeddings pour suggérer des films pertinents aux utilisateurs. Le système analyse les métadonnées des films (synopsis, genre, année de sortie, durée, producteur, etc.) et les transforme en vecteurs pour permettre des recommandations précises et personnalisées à travers des mesures de similarité.

## Architecture Technique

Le projet est construit autour des technologies suivantes :

- **Qdrant** : Base de données vectorielles pour le stockage et la recherche efficace des embeddings
- **Firebase** : Stockage des métadonnées des films et gestion des utilisateurs
- **Streamlit** : Application web pour l'interface utilisateur et le backend
- **LangChain** : Framework pour la gestion des pipelines de vectorisation et de gestion des embeddings
- **Ollama** : Serveur de LLM (Large Language Model) pour l'exécution locale des modèles de langage

## Fonctionnalités

- Vectorisation des métadonnées de films pour une recherche sémantique
- Recommandations personnalisées basées sur les préférences de l'utilisateur
- Recherche de films similaires à partir d'un film donné
- Interface utilisateur intuitive pour explorer le catalogue de films
- Administration simple pour ajouter de nouveaux films

## Installation

### Prérequis

- Docker Desktop `https://docs.docker.com/desktop/setup/install/windows-install/`
- Git `https://git-scm.com/downloads/win`
- Python >=3.11

### Étapes d'installation

1. Clonez le dépôt :
```bash

git clone https://github.com/balh495/movie-recommender.git
cd movie-recommender
```

2. Lancez les émulateurs Firebase :
```bash

cd firebase
firebase emulators:start --import=./emulator-data --export-on-exit
```

3. Lancez l'application avec Docker Compose :

Placez-vous dans le dossier `movie-recommender/backend`

```bash

cd backend
docker compose up [--build]
```

4. Accédez aux différentes interfaces :
   - Application Streamlit : http://localhost:8501
   - Firebase Emulator UI : http://localhost:8080
   - Qdrant UI : http://localhost:6333/dashboard

## Utilisation

### Fonctionnalités de l'Application

L'application Streamlit permet de :

- Parcourir le catalogue de films
- Rechercher des films par titre, genre, ou autres critères
- Voir les détails d'un film spécifique
- Obtenir des recommandations personnalisées
- Ajouter de nouveaux films au catalogue

### Pages de l'Application

- **Accueil** : Présentation du système et statut des connexions
- **Recommandations** : Recherche de films similaires à partir d'un texte
- **Catalogue** : Liste des films disponibles avec possibilité de voir des recommandations similaires
- **Administration** : Ajout de nouveaux films et tests de connexion
