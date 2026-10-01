"""Phase 3: Store embeddings in persistent ChromaDB."""

import os
import chromadb
from chromadb.config import Settings

# Persistent storage location
VECTOR_DB_DIR = "vector_db"

# Collection name for document chunks
COLLECTION_NAME = "hdfc_mutual_funds"


def get_chroma_client():
    """Create and return a persistent ChromaDB client.

    The client uses disk-based persistence, so data survives restarts.

    Returns:
        chromadb.PersistentClient: The ChromaDB client.
    """
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR,
        settings=Settings(anonymized_telemetry=False),
    )
    return client


def get_or_create_collection(client):
    """Get the existing collection or create a new one.

    If the collection already exists and has data, it is returned as-is.
    This prevents duplicate ingestion on subsequent runs.

    Args:
        client: The ChromaDB client.

    Returns:
        chromadb.Collection: The collection for document chunks.
    """
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        count = collection.count()
        if count > 0:
            print(f"Collection '{COLLECTION_NAME}' already exists with {count} items. Skipping re-ingestion.")
        return collection
    except Exception:
        pass

    # Create new collection with cosine similarity
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"Created new collection '{COLLECTION_NAME}'.")
    return collection


def add_chunks_to_collection(collection, ids, embeddings, documents, metadatas):
    """Add chunk embeddings and metadata to the collection.

    Args:
        collection: The ChromaDB collection.
        ids: List of chunk IDs.
        embeddings: List of embedding vectors.
        documents: List of chunk text strings.
        metadatas: List of metadata dicts.
    """
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    print(f"Added {len(ids)} chunks to collection.")


def get_collection_count(collection):
    """Return the number of items in the collection.

    Args:
        collection: The ChromaDB collection.

    Returns:
        int: Number of items stored.
    """
    return collection.count()
