"""Phase 3: Embed text chunks using sentence-transformers/all-MiniLM-L6-v2."""

import os

# Fix for Windows Application Control policy blocking torch DLLs
_torch_lib = os.path.join(os.path.dirname(os.__file__), "Lib", "site-packages", "torch", "lib")
if os.path.isdir(_torch_lib):
    os.add_dll_directory(_torch_lib)

from sentence_transformers import SentenceTransformer

# Model name — must be the same for ingestion and query
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Singleton model instance (loaded once, reused across calls)
_model = None


def get_model():
    """Load and return the singleton embedding model.

    The model is loaded only once and reused for all subsequent calls.
    This ensures consistency and avoids reloading overhead.

    Returns:
        SentenceTransformer: The loaded all-MiniLM-L6-v2 model.
    """
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        print(f"Model loaded. Embedding dimension: {_model.get_sentence_embedding_dimension()}")
    return _model


def embed_text(text):
    """Embed a single text string into a vector.

    Args:
        text: The text to embed.

    Returns:
        list[float]: The embedding vector.
    """
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_texts(texts):
    """Embed a list of text strings into vectors.

    Args:
        texts: List of text strings to embed.

    Returns:
        list[list[float]]: List of embedding vectors.
    """
    model = get_model()
    return model.encode(texts, normalize_embeddings=True).tolist()


def get_embedding_dimension():
    """Return the embedding dimension of the model.

    Returns:
        int: The dimension of the embedding vectors (384 for all-MiniLM-L6-v2).
    """
    model = get_model()
    return model.get_sentence_embedding_dimension()
