"""Phase 5: Retrieve relevant chunks from ChromaDB."""

import os

# Fix for Windows Application Control policy blocking torch DLLs
_torch_lib = os.path.join(os.path.dirname(os.__file__), "Lib", "site-packages", "torch", "lib")
if os.path.isdir(_torch_lib):
    os.add_dll_directory(_torch_lib)

from ingestion.store import get_chroma_client, get_or_create_collection, COLLECTION_NAME


def retrieve_chunks(question_embedding, top_k=5):
    """Retrieve the most relevant chunks from ChromaDB.

    Args:
        question_embedding: The embedding vector of the user's question.
        top_k: Number of chunks to retrieve (default: 5).

    Returns:
        list[dict]: List of retrieved chunks with keys:
            - 'text': The chunk text
            - 'source_url': The source URL
            - 'scheme_name': The scheme name
            - 'source_title': The source title
            - 'similarity': The cosine similarity score
    """
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    if results and results["ids"] and len(results["ids"]) > 0:
        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(ids)):
            # Convert distance to similarity (ChromaDB uses cosine distance)
            similarity = 1.0 - distances[i]
            chunks.append({
                "text": documents[i],
                "source_url": metadatas[i].get("source_url", ""),
                "scheme_name": metadatas[i].get("scheme_name", ""),
                "source_title": metadatas[i].get("source_title", ""),
                "similarity": similarity,
            })

    return chunks


def get_similarity_scores(chunks):
    """Extract similarity scores from retrieved chunks.

    Args:
        chunks: List of chunk dicts from retrieve_chunks.

    Returns:
        list[float]: List of similarity scores.
    """
    return [chunk["similarity"] for chunk in chunks]


# Navigation noise keywords that indicate a chunk is mostly menu/navigation text
NAVIGATION_KEYWORDS = [
    "invest in stocks", "intraday", "etf screener", "ipo", "mtf", "stock screener",
    "stock events", "demat account", "share market today", "f&o", "trade in futures",
    "indices", "track markets", "terminal", "track charts", "option chain",
    "analyse chains", "pledge", "get extra balance", "commodities", "trade in crude",
    "api trading", "mutual fund houses", "know about amcs", "nfo", "track all active",
    "mutual funds by groww", "start sip", "build long-term wealth",
    "mutual funds screener", "filter funds", "track funds", "import funds",
    "compare funds", "sip calculator", "brokerage calculator", "margin calculator",
    "swp calculator", "returns on your systematic", "pricing", "brokerage and charges",
    "blog", "credit", "loan against securities", "personal loan",
    "download the app", "about us", "media & press", "careers", "help & support",
    "trust & safety", "investor relations", "products", "stocks", "f&o", "mtf",
    "etf", "ipo", "mutual funds", "commodities", "groww terminal", "915 terminal",
    "stock screens", "algo trading", "groww charts", "groww digest", "groww amc",
    "pms", "bonds", "credit", "nri demat", "huf demat", "minor demat",
    "share market live", "fii dii activity", "stocks sectors", "top gainers",
    "52 weeks high", "top losers", "52 weeks low", "most traded",
    "stocks market calender", "stocks feed", "share market live update",
    "stock average calculator", "epf calculator", "tds calculator", "mf calculator",
    "ssy calculator", "income tax calculator", "emi calculator", "step-up sip",
    "ppf calculator", "gst calculator", "car loan", "what is ipo",
    "how to apply for an ipo", "open ipos", "what is grey market",
    "upcoming ipos", "mainboard ipos", "closed ipos", "sme ipos",
    "ipo subscription", "ipo allotment", "pricing", "trust & safety",
    "groww digest", "minor demat", "intraday", "blog", "investor relations",
    "invest in gold", "corporate bonds", "media & press", "gold rates",
    "invest in silver", "careers", "silver rates", "sitemap", "about us",
    "help & support", "glossary", "nri demat", "show more", "others:",
    "nse", "bse", "mcx", "terms and conditions", "policies and procedures",
    "regulatory & other info", "privacy policy", "disclosure", "smart odr",
    "download forms", "information security practices", "investor charter",
    "grievance", "bug bounty", "groww pay", "groww ifsc",
]


def is_navigation_noise(chunk_text):
    """Check if a chunk is dominated by navigation/menu noise.

    Args:
        chunk_text: The text content of a chunk.

    Returns:
        bool: True if the chunk is mostly navigation noise.
    """
    text_lower = chunk_text.lower()
    words = text_lower.split()
    if len(words) < 5:
        return False

    # Count how many navigation keywords appear
    nav_count = sum(1 for keyword in NAVIGATION_KEYWORDS if keyword in text_lower)

    # If 3+ navigation keywords found, consider it noise
    return nav_count >= 3


def filter_chunks(chunks):
    """Remove chunks that are dominated by navigation noise.

    Args:
        chunks: List of chunk dicts.

    Returns:
        list[dict]: Filtered list of chunks.
    """
    filtered = [c for c in chunks if not is_navigation_noise(c["text"])]
    return filtered if filtered else chunks  # Return original if all filtered out
