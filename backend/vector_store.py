import os
from qdrant_client import QdrantClient
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

def init_vector_store(collection_name="movies"):
    """
    Initialise le client Qdrant et les embeddings Ollama,
    puis retourne un QdrantVectorStore utilisable.
    """

    # Qdrant
    qdrant_host = os.environ.get("QDRANT_HOST", "localhost")
    qdrant_port = int(os.environ.get("QDRANT_PORT", 6333))
    qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

    # Ollama embeddings
    ollama_host = os.environ.get("OLLAMA_HOST", "localhost")
    ollama_port = int(os.environ.get("OLLAMA_PORT", 11434))
    ollama_url = f"http://{ollama_host}:{ollama_port}"
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    if collection_name not in [col.name for col in qdrant_client.get_collections().collections]:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "size": 512,
                "distance": "Cosine"
            }
        )

    # base_url=ollama_url, 
    # Vector store
    return QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embeddings
    )
