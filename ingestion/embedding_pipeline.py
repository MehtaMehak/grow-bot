"""Phase 3: Embedding pipeline — embed chunks and store in ChromaDB."""

import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.embedder import embed_texts, get_embedding_dimension
from ingestion.store import (
    get_chroma_client,
    get_or_create_collection,
    add_chunks_to_collection,
    get_collection_count,
    COLLECTION_NAME,
    VECTOR_DB_DIR,
)

# Path to the chunks file from Phase 2
CHUNKS_PATH = "data/chunks/chunks.txt"

# Path for the embeddings preview output
PREVIEW_PATH = "data/embeddings_preview.txt"

# Number of embedding previews to write
PREVIEW_COUNT = 5

# Number of dimensions to show in preview
PREVIEW_DIMS = 10


def load_chunks(chunks_path):
    """Load chunks from the JSON Lines file.

    Args:
        chunks_path: Path to the chunks file.

    Returns:
        list[dict]: List of chunk records.
    """
    chunks = []
    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def write_embedding_preview(chunks, embeddings, preview_path):
    """Write a preview of the first N embeddings to a text file.

    Args:
        chunks: List of chunk records.
        embeddings: List of embedding vectors.
        preview_path: Path to write the preview file.
    """
    lines = []
    lines.append("=" * 80)
    lines.append("EMBEDDING PREVIEW")
    lines.append("=" * 80)
    lines.append(f"Model: sentence-transformers/all-MiniLM-L6-v2")
    lines.append(f"Embedding dimension: {len(embeddings[0])}")
    lines.append(f"Total chunks embedded: {len(embeddings)}")
    lines.append(f"Preview: First {PREVIEW_COUNT} chunks, first {PREVIEW_DIMS} dimensions each")
    lines.append("")

    for i in range(min(PREVIEW_COUNT, len(chunks))):
        chunk = chunks[i]
        embedding = embeddings[i]
        preview_dims = embedding[:PREVIEW_DIMS]

        lines.append("-" * 80)
        lines.append(f"Chunk #{i + 1}")
        lines.append(f"  Chunk ID:     {chunk['chunk_id']}")
        lines.append(f"  Scheme Name:  {chunk['scheme_name']}")
        lines.append(f"  Source URL:   {chunk['source_url']}")
        lines.append(f"  Chunk Index:  {chunk['chunk_index']}")
        lines.append(f"  Char Count:   {len(chunk['chunk_text'])}")
        lines.append(f"  Embedding (first {PREVIEW_DIMS} dims):")
        lines.append(f"    {preview_dims}")
        lines.append("")

    lines.append("-" * 80)
    lines.append("End of embedding preview")
    lines.append("=" * 80)

    output = "\n".join(lines)

    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Embedding preview written to: {preview_path}")


def main():
    print("=" * 70)
    print("PHASE 3 — EMBEDDING & VECTOR STORE")
    print("=" * 70)

    # Step 1: Load chunks from Phase 2
    print(f"\nLoading chunks from: {CHUNKS_PATH}")
    chunks = load_chunks(CHUNKS_PATH)
    print(f"Loaded {len(chunks)} chunks.")

    # Step 2: Initialize ChromaDB
    print(f"\nInitializing ChromaDB at: {VECTOR_DB_DIR}")
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    # Check if collection already has data
    existing_count = get_collection_count(collection)
    if existing_count > 0:
        print(f"\nCollection already has {existing_count} items.")
        print("Skipping re-ingestion to avoid duplicates.")
        print(f"Collection '{COLLECTION_NAME}' is ready for querying.")
        print("=" * 70)
        return

    # Step 3: Embed all chunks
    print(f"\nEmbedding {len(chunks)} chunks...")
    texts = [c["chunk_text"] for c in chunks]
    embeddings = embed_texts(texts)
    print(f"Embedding complete. Dimension: {len(embeddings[0])}")

    # Step 4: Prepare data for ChromaDB
    # Re-number chunk IDs to be globally unique (original IDs restart per source)
    ids = [f"chunk_{i + 1:06d}" for i in range(len(chunks))]
    documents = [c["chunk_text"] for c in chunks]
    metadatas = [
        {
            "source_url": c["source_url"],
            "source_type": c["source_type"],
            "scheme_name": c["scheme_name"],
            "source_title": c["source_title"],
            "document_date": c.get("document_date") or "",
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]

    # Step 5: Store in ChromaDB
    print(f"\nStoring embeddings in ChromaDB...")
    add_chunks_to_collection(collection, ids, embeddings, documents, metadatas)

    # Step 6: Write embedding preview
    print(f"\nWriting embedding preview...")
    write_embedding_preview(chunks, embeddings, PREVIEW_PATH)

    # Step 7: Summary
    final_count = get_collection_count(collection)
    print("\n" + "=" * 70)
    print("PHASE 3 SUMMARY")
    print("=" * 70)
    print(f"Chunks embedded: {final_count}")
    print(f"Embedding dimension: {len(embeddings[0])}")
    print(f"ChromaDB collection: {COLLECTION_NAME}")
    print(f"Persistence location: {os.path.abspath(VECTOR_DB_DIR)}")
    print(f"Vector DB persists after restart: Yes")
    print("=" * 70)


if __name__ == "__main__":
    main()
