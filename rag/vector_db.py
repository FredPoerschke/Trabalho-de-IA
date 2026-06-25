import os
import threading
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

# Configurações de caminhos e nomes da coleção
CHROMA_PATH = os.getenv("CHROMA_PATH", "rag/chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "boas_praticas_codigo")

# Singleton thread-safe para evitar erro de concorrência no PersistentClient do CrewAI
_client: chromadb.ClientAPI | None = None
_lock = threading.Lock()


def get_embedding_function() -> OllamaEmbeddingFunction:
    """
    Configura a função de embedding usando o Ollama local.
    Certifique-se de ter rodado 'ollama run nomic-embed-text' na sua máquina.
    """
    return OllamaEmbeddingFunction(
        url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model_name=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
    )


def get_chroma_client() -> chromadb.ClientAPI:
    """
    Retorna a instância única do cliente ChromaDB.
    Se a instância não existir, cria uma nova de forma thread-safe.
    """
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _client


def get_collection(client: chromadb.ClientAPI | None = None) -> chromadb.Collection:
    """
    Recupera ou cria a coleção no banco vetorial onde os manuais estão armazenados.
    Esta é a função que as suas Tools irão importar.
    """
    client = client or get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
    )