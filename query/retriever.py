"""Phase 5: Retrieve relevant chunks from ChromaDB."""

import os

# Fix for Windows Application Control policy blocking torch DLLs
_torch_lib = os.path.join(
    os.path.dirname(os.__file__),
    "Lib",
    "site-packages",
    "torch",
    "lib",
)

if os.path.isdir(_torch_lib):
    os.add_dll_directory(_torch_lib)

from ingestion.store import (
    get_chroma_client,
    get_or_create_collection,
    COLLECTION_NAME,
)


def retrieve_chunks(question_embedding, top_k=5):
    """Retrieve the most relevant chunks from ChromaDB.

    Args:
        question_embedding: The embedding vector of the user's question.
        top_k: Number of chunks to retrieve.

    Returns:
        list[dict]: Retrieved chunks with text, metadata, and similarity.
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
            # ChromaDB returns cosine distance.
            # Convert distance to similarity.
            similarity = 1.0 - distances[i]

            chunks.append(
                {
                    "text": documents[i],
                    "source_url": metadatas[i].get("source_url", ""),
                    "scheme_name": metadatas[i].get("scheme_name", ""),
                    "source_title": metadatas[i].get("source_title", ""),
                    "similarity": similarity,
                }
            )

    return chunks


def get_similarity_scores(chunks):
    """Extract similarity scores from retrieved chunks."""

    return [chunk["similarity"] for chunk in chunks]


# Navigation noise keywords that indicate a chunk is mostly menu/navigation text
NAVIGATION_KEYWORDS = [
    "invest in stocks",
    "intraday",
    "etf screener",
    "ipo",
    "mtf",
    "stock screener",
    "stock events",
    "demat account",
    "share market today",
    "f&o",
    "trade in futures",
    "indices",
    "track markets",
    "terminal",
    "track charts",
    "option chain",
    "analyse chains",
    "pledge",
    "get extra balance",
    "commodities",
    "trade in crude",
    "api trading",
    "mutual fund houses",
    "know about amcs",
    "nfo",
    "track all active",
    "mutual funds by groww",
    "start sip",
    "build long-term wealth",
    "mutual funds screener",
    "filter funds",
    "track funds",
    "import funds",
    "compare funds",
    "sip calculator",
    "brokerage calculator",
    "margin calculator",
    "swp calculator",
    "returns on your systematic",
    "pricing",
    "brokerage and charges",
    "blog",
    "credit",
    "loan against securities",
    "personal loan",
    "download the app",
    "about us",
    "media & press",
    "careers",
    "help & support",
    "trust & safety",
    "investor relations",
    "products",
    "stocks",
    "etf",
    "groww terminal",
    "915 terminal",
    "stock screens",
    "algo trading",
    "groww charts",
    "groww digest",
    "groww amc",
    "pms",
    "bonds",
    "nri demat",
    "huf demat",
    "minor demat",
    "share market live",
    "fii dii activity",
    "stocks sectors",
    "top gainers",
    "52 weeks high",
    "top losers",
    "52 weeks low",
    "most traded",
    "stocks market calender",
    "stocks feed",
    "share market live update",
    "stock average calculator",
    "epf calculator",
    "tds calculator",
    "mf calculator",
    "ssy calculator",
    "income tax calculator",
    "emi calculator",
    "step-up sip",
    "ppf calculator",
    "gst calculator",
    "car loan",
    "what is ipo",
    "how to apply for an ipo",
    "open ipos",
    "what is grey market",
    "upcoming ipos",
    "mainboard ipos",
    "closed ipos",
    "sme ipos",
    "ipo subscription",
    "ipo allotment",
    "groww digest",
    "invest in gold",
    "corporate bonds",
    "media & press",
    "gold rates",
    "invest in silver",
    "silver rates",
    "sitemap",
    "glossary",
    "show more",
    "others:",
    "nse",
    "bse",
    "mcx",
    "terms and conditions",
    "policies and procedures",
    "regulatory & other info",
    "privacy policy",
    "disclosure",
    "smart odr",
    "download forms",
    "information security practices",
    "investor charter",
    "grievance",
    "bug bounty",
    "groww pay",
    "groww ifsc",
]


def is_navigation_noise(chunk_text):
    """Check if a chunk is dominated by navigation/menu noise.

    Important fund-specific facts are always preserved.
    """

    text_lower = chunk_text.lower()

    # Never filter chunks containing important fund-specific facts.
    fund_fact_keywords = [
        "lock-in period",
        "expense ratio",
        "exit load",
        "minimum investment",
        "minimum additional investment",
        "fund manager",
        "benchmark",
        "aum",
        "nav",
        "holdings",
        "portfolio",
        "objective",
        "investment objective",
        "asset allocation",
        "riskometer",
        "fund information",
        "scheme information",
    ]

    if any(
        keyword in text_lower
        for keyword in fund_fact_keywords
    ):
        return False

    words = text_lower.split()

    if len(words) < 5:
        return False

    nav_count = sum(
        1
        for keyword in NAVIGATION_KEYWORDS
        if keyword in text_lower
    )

    return nav_count >= 3


def filter_chunks(chunks):
    """Remove chunks that are dominated by navigation noise."""

    filtered = [
        chunk
        for chunk in chunks
        if not is_navigation_noise(chunk["text"])
    ]

    # If every chunk was filtered, return the original chunks.
    return filtered if filtered else chunks