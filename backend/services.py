import streamlit as st

def get_movies(db):
    """
    Récupère tous les films stockés dans Firestore.
    Retourne {success: bool, data: list | error: str}
    """
    try:
        movies_ref = db.collection("movies")
        movies = [doc.to_dict() for doc in movies_ref.stream()]
        return {"success": True, "data": movies}
    except Exception as e:
        return {"success": False, "error": str(e)}

def add_movie(db, vector_store, movie_data):
    """
    Ajoute un film à Firestore + au vector store si dispo.
    """
    try:
        if not movie_data or not movie_data.get("title"):
            return {"success": False, "error": "Titre du film requis"}

        movie_ref = db.collection("movies").document()
        movie_data["id"] = movie_ref.id
        movie_ref.set(movie_data)

        # Indexation dans le vector store
        if vector_store:
            try:
                movie_text = f"Title: {movie_data.get('title', '')}\n"
                if "description" in movie_data:
                    movie_text += f"Description: {movie_data['description']}\n"
                if "genre" in movie_data:
                    movie_text += f"Genre: {movie_data['genre']}\n"

                vector_store.add_texts(
                    texts=[movie_text],
                    metadatas=[{"id": movie_data["id"], "title": movie_data.get("title", "")}],
                    ids=[movie_data["id"]]
                )
            except Exception as e:
                st.warning(f"Ajouté à Firestore mais échec d’indexation: {str(e)}")

        return {"success": True, "data": movie_data, "id": movie_ref.id}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_recommendations(vector_store, query_text, n=3):
    """
    Retourne les recommandations de films à partir d’un texte.
    Utilise la recherche par similarité dans Qdrant.
    """
    try:
        if not vector_store:
            return {"success": False, "error": "Vector store indisponible"}

        results = vector_store.similarity_search_with_score(query_text, k=n)

        recommendations = []
        for doc, score in results:
            similarity = 1.0 - min(score, 1.0)
            recommendations.append({
                "id": doc.metadata.get("id", "unknown"),
                "title": doc.metadata.get("title", "Unknown Title"),
                "similarity": round(similarity, 2),
            })

        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_firebase_connection(db):
    """
    Vérifie que Firestore est bien accessible.
    """
    try:
        test_ref = db.collection("test").document("connection")
        test_ref.set({"message": "ok"})
        return {"success": True, "message": "Connexion Firebase OK"}
    except Exception as e:
        return {"success": False, "message": "Connexion Firebase échouée", "error": str(e)}
