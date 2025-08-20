import streamlit as st
from firebase_client import init_firestore
from vector_store import init_vector_store
from services import get_movies, add_movie, get_recommendations, test_firebase_connection

st.set_page_config(
    page_title="Movie Recommender",
    layout="wide"
)

# --- Initialisation ---
db = init_firestore()
try:
    vector_store = init_vector_store("movies")
except Exception as e:
    st.warning(f"Vector store non disponible: {str(e)}")
    vector_store = None

# --- UI ---
st.title("Movie Recommender")
st.markdown("Système de recommandation de films basé sur Firestore, Qdrant et Ollama.")

page = st.sidebar.radio("Navigation", ["Accueil", "Recommandations", "Catalogue", "Administration"])

if page == "Accueil":
    st.header("Bienvenue")
    firebase_status = test_firebase_connection(db)
    if firebase_status.get("success"):
        st.success("Firebase connecté")
    else:
        st.error("Firebase non connecté")

    if vector_store:
        st.success("Qdrant & Ollama connectés")
    else:
        st.error("Qdrant/Ollama non disponibles")

elif page == "Recommandations":
    query = st.text_input("Entrez un film ou une description:")
    if st.button("Rechercher") and query:
        results = get_recommendations(vector_store, query, n=5)
        if results.get("success") and results.get("recommendations"):
            for movie in results["recommendations"]:
                st.write(f"{movie['title']} (Similarité: {movie['similarity']})")
        else:
            st.info("Aucune recommandation trouvée.")

elif page == "Catalogue":
    movies = get_movies(db)
    if movies.get("success"):
        for movie in movies["data"]:
            st.subheader(movie.get("title", "Sans titre"))
            st.write(movie.get("description", ""))
    else:
        st.warning("Impossible de charger le catalogue")

elif page == "Administration":
    with st.form("add_movie_form"):
        title = st.text_input("Titre")
        description = st.text_area("Description")
        genre = st.text_input("Genre")
        year = st.number_input("Année", min_value=1900, max_value=2100, value=2023)

        if st.form_submit_button("Ajouter"):
            result = add_movie(db, vector_store, {
                "title": title,
                "description": description,
                "genre": genre,
                "year": year,
            })
            if result.get("success"):
                st.success("Film ajouté")
            else:
                st.error(result.get("error", "Erreur inconnue"))
