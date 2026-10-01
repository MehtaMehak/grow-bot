"""Chunk raw text into smaller pieces with overlap and metadata."""

import json


def chunk_text(text, chunk_size=500, overlap=100):
    """Split text into chunks with overlap.

    Args:
        text: The raw text to chunk.
        chunk_size: Maximum characters per chunk (default 500).
        overlap: Characters of overlap between consecutive chunks (default 100).

    Returns:
        List of chunk strings.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def create_chunks(source_data, chunk_size=500, overlap=100):
    """Create chunk records from source data.

    Args:
        source_data: dict with keys: raw_text, source_url, source_type,
                     scheme_name, source_title, document_date
        chunk_size: Maximum characters per chunk (default 500).
        overlap: Characters of overlap between consecutive chunks (default 100).

    Returns:
        List of chunk record dicts.
    """
    raw_text = source_data["raw_text"]
    text_chunks = chunk_text(raw_text, chunk_size, overlap)

    chunk_records = []
    for i, chunk_text_content in enumerate(text_chunks):
        record = {
            "chunk_id": f"chunk_{len(chunk_records) + 1:06d}",
            "source_url": source_data["source_url"],
            "source_type": source_data["source_type"],
            "scheme_name": source_data["scheme_name"],
            "source_title": source_data["source_title"],
            "document_date": source_data.get("document_date"),
            "chunk_index": i,
            "chunk_text": chunk_text_content,
        }
        chunk_records.append(record)

    return chunk_records


def save_chunks_to_file(chunk_records, output_path):
    """Save chunk records to a JSON Lines file.

    Args:
        chunk_records: List of chunk record dicts.
        output_path: Path to the output file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for record in chunk_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
