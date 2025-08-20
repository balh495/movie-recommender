import streamlit as st
import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK
# For local development with emulators
# Always use emulator mode for local development
# Force using emulator without credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

# Create a dummy credential that doesn't try to look up default credentials
dummy_cred = credentials.ApplicationDefaultCredential(None)
firebase_admin.initialize_app(dummy_cred, {
    'projectId': 'movie-recommender',
})
print(f"Initialized Firebase with emulator at {os.environ.get('FIRESTORE_EMULATOR_HOST', 'default emulator')}")

# Get Firestore client
db = firestore.client()

# Initialize Qdrant client
qdrant_host = os.environ.get('QDRANT_HOST', 'localhost')
qdrant_port = int(os.environ.get('QDRANT_PORT', 6333))
qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

# Initialize Ollama embeddings
ollama_host = os.environ.get('OLLAMA_HOST', 'localhost')
ollama_port = int(os.environ.get('OLLAMA_PORT', 11434))
ollama_url = f"http://{ollama_host}:{ollama_port}"
embeddings = OllamaEmbeddings(base_url=ollama_url, model="nomic-embed-text")

# Initialize vector store
collection_name = "movies"
try:
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embeddings=embeddings
    )
except Exception as e:
    st.error(f"Error initializing vector store: {str(e)}")
    vector_store = None

# Set page title and configuration
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("Movie Recommender")
st.markdown("Système de recommendation de film basé sur les métadonnées et le traitement du langage naturel.")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Accueil", "Recommandations", "Catalogue", "Administration"])

# Function to get all movies from Firestore
def get_movies():
    try:
        movies_ref = db.collection('movies')
        movies = [doc.to_dict() for doc in movies_ref.stream()]
        return {"success": True, "data": movies}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Function to add a movie to Firestore
def add_movie(movie_data):
    try:
        # Validate required fields
        if not movie_data or not movie_data.get('title'):
            return {"success": False, "error": "Movie title is required"}

        # Add movie to Firestore
        movie_ref = db.collection('movies').document()
        movie_data['id'] = movie_ref.id
        movie_ref.set(movie_data)

        # Add to vector store if available
        if vector_store:
            try:
                # Create a text representation of the movie for embedding
                movie_text = f"Title: {movie_data.get('title', '')}\n"
                if 'description' in movie_data:
                    movie_text += f"Description: {movie_data.get('description', '')}\n"
                if 'genre' in movie_data:
                    movie_text += f"Genre: {movie_data.get('genre', '')}\n"

                # Add to vector store
                vector_store.add_texts(
                    texts=[movie_text],
                    metadatas=[{"id": movie_data['id'], "title": movie_data.get('title', '')}],
                    ids=[movie_data['id']]
                )
            except Exception as e:
                st.warning(f"Added to Firestore but failed to add to vector store: {str(e)}")

        return {"success": True, "data": movie_data, "id": movie_ref.id}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Function to get movie recommendations
def get_recommendations(query_text, n=3):
    try:
        if not vector_store:
            return {"success": False, "error": "Vector store not available"}

        results = vector_store.similarity_search_with_score(query_text, k=n)

        recommendations = []
        for doc, score in results:
            # Convert score to similarity (scores from Qdrant are distances, lower is better)
            similarity = 1.0 - min(score, 1.0)  # Normalize to 0-1 range

            recommendations.append({
                "id": doc.metadata.get("id", "unknown"),
                "title": doc.metadata.get("title", "Unknown Title"),
                "similarity": round(similarity, 2)
            })

        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Function to test Firebase connection
def test_firebase_connection():
    try:
        # Try to access Firestore
        test_ref = db.collection('test').document('connection')
        test_ref.set({
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'Firebase connection successful'
        })

        test_data = test_ref.get().to_dict()

        return {
            "success": True, 
            "message": "Firebase connection successful",
            "data": test_data
        }
    except Exception as e:
        return {
            "success": False, 
            "message": "Firebase connection failed", 
            "error": str(e)
        }

# Main content
if page == "Accueil":
    st.header("Bienvenue sur Movie Recommender")
    st.write("""
    Ce système utilise des techniques avancées de traitement du langage naturel 
    pour vous recommander des films pertinents en fonction de vos préférences.
    """)

    st.subheader("Comment ça marche")
    st.write("""
    1. Parcourez notre catalogue de films
    2. Sélectionnez un film que vous aimez
    3. Obtenez des recommandations personnalisées
    """)

    # Display system status
    st.subheader("État du système")
    col1, col2 = st.columns(2)

    with col1:
        firebase_status = test_firebase_connection()
        if firebase_status.get("success"):
            st.success("✅ Firebase connecté")
        else:
            st.error(f"❌ Firebase non connecté: {firebase_status.get('error', '')}")

    with col2:
        if vector_store:
            st.success("✅ Qdrant & Ollama connectés")
        else:
            st.error("❌ Qdrant ou Ollama non connectés")

elif page == "Recommandations":
    st.header("Recommandations de films")

    # Input for search query
    query = st.text_input("Rechercher des films similaires à:", "")

    if st.button("Rechercher") and query:
        with st.spinner("Recherche en cours..."):
            results = get_recommendations(query, n=5)

            if results.get("success") and results.get("recommendations"):
                st.subheader("Films recommandés")
                for movie in results.get("recommendations", []):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image("https://via.placeholder.com/150x225", caption="Affiche")
                    with col2:
                        st.subheader(movie["title"])
                        st.write(f"Similarité: {movie['similarity']}")
                        if st.button(f"Voir détails", key=f"details_{movie['id']}"):
                            st.session_state.selected_movie_id = movie['id']
                            st.session_state.page = "Catalogue"
                    st.divider()
            else:
                st.info("Aucune recommandation trouvée. Essayez une autre recherche.")

elif page == "Catalogue":
    st.header("Catalogue de films")

    movies = get_movies()
    if movies and movies.get("success"):
        movie_list = movies.get("data", [])
        if movie_list:
            for movie in movie_list:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image("https://via.placeholder.com/150x225", caption="Affiche")
                with col2:
                    st.subheader(movie.get("title", "Sans titre"))
                    if "description" in movie:
                        st.write(movie["description"])
                    if st.button(f"Recommander des films similaires", key=f"similar_{movie.get('id', '')}"):
                        query_text = f"Title: {movie.get('title', '')}\n"
                        if 'description' in movie:
                            query_text += f"Description: {movie.get('description', '')}\n"

                        with st.spinner("Recherche en cours..."):
                            results = get_recommendations(query_text, n=3)

                            if results.get("success") and results.get("recommendations"):
                                st.subheader("Films similaires")
                                for rec_movie in results.get("recommendations", []):
                                    if rec_movie["id"] != movie.get("id", ""):  # Don't recommend the same movie
                                        st.write(f"- {rec_movie['title']} (Similarité: {rec_movie['similarity']})")
                            else:
                                st.info("Aucune recommandation trouvée.")
                st.divider()
        else:
            st.info("Aucun film dans le catalogue pour le moment.")
    else:
        st.warning(f"Impossible de charger le catalogue: {movies.get('error', 'Erreur inconnue')}")

elif page == "Administration":
    st.header("Administration")

    # Add new movie form
    st.subheader("Ajouter un nouveau film")
    with st.form("add_movie_form"):
        title = st.text_input("Titre")
        description = st.text_area("Description")
        genre = st.text_input("Genre")
        year = st.number_input("Année", min_value=1900, max_value=2100, value=2023)

        submitted = st.form_submit_button("Ajouter")
        if submitted:
            movie_data = {
                "title": title,
                "description": description,
                "genre": genre,
                "year": year
            }

            result = add_movie(movie_data)
            if result.get("success"):
                st.success(f"Film ajouté avec succès! ID: {result.get('id')}")
            else:
                st.error(f"Erreur lors de l'ajout du film: {result.get('error')}")

    # Test connections
    st.subheader("Tester les connexions")
    if st.button("Tester Firebase"):
        result = test_firebase_connection()
        if result.get("success"):
            st.success("Connexion à Firebase réussie!")
            st.json(result.get("data", {}))
        else:
            st.error(f"Erreur de connexion à Firebase: {result.get('error')}")

# Footer
st.markdown("---")
st.markdown("© 2025 Movie Recommender - Tous droits réservés")
