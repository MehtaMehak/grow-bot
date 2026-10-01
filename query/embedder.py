"""Phase 5: Embed user questions using the same model as Phase 3.

This module reuses the embedding model from ingestion.embedder to ensure
the same vector space is used for both document chunks and user questions.
"""

import os

# Fix for Windows Application Control policy blocking torch DLLs
_torch_lib = os.path.join(os.path.dirname(os.__file__), "Lib", "site-packages", "torch", "lib")
if os.path.isdir(_torch_lib):
    os.add_dll_directory(_torch_lib)

from ingestion.embedder import get_model


def embed_question(question):
    """Embed a user question into a vector using the same model as Phase 3.

    Args:
        question: The user's question string.

    Returns:
        list[float]: The embedding vector (384 dimensions).
    """
    model = get_model()
    return model.encode(question, normalize_embeddings=True).tolist()
