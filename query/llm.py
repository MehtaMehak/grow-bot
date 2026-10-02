"""Phase 5: Generate answers using Groq API."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")


def validate_config():
    """Validate that Groq configuration is present.

    Raises:
        ValueError: If GROQ_API_KEY or GROQ_MODEL is missing.
    """
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Please add it to your .env file."
        )
    if not GROQ_MODEL:
        raise ValueError(
            "GROQ_MODEL is not set. Please add it to your .env file. "
            "Do not assume a default model name."
        )


def build_system_prompt():
    """Build the strict system prompt for the LLM.

    Returns:
        str: The system prompt.
    """
    return (
        "You are a factual assistant for HDFC mutual fund information. "
        "Your answers must follow these rules strictly:\n"
        "1. Answer ONLY from the provided source context. Do not use outside knowledge.\n"
        "2. Keep answers factual and educational. Maximum 3 sentences.\n"
        "3. Include exactly one relevant source link from the context.\n"
        "4. End your answer with 'Last updated from sources: [URL]' where [URL] is the source link.\n"
        "5. Do NOT provide investment advice or recommendations.\n"
        "6. Do NOT calculate or claim investment returns or performance.\n"
        "7. If the context does not contain the answer, say: "
        "'I don't know based on the available sources.'\n"
        "8. Do not invent facts or sources. Only use what is in the context.\n"
        "9. Always provide a substantive answer when the context contains relevant information. "
        "Do not return an empty response.\n"
        "10. The source text may contain website navigation menu items "
        "(e.g., 'Stocks', 'F&O', 'IPO', 'SIP calculator', 'Blog', 'Pricing', etc.). "
        "IGNORE these navigation items and focus ONLY on fund-specific factual information "
        "such as expense ratio, exit load, NAV, AUM, holdings, fund manager, benchmark, "
        "minimum investment, lock-in period, and other scheme details.\n"
    )


def build_user_message(question, chunks):
    """Build the user message with question and context.

    Args:
        question: The user's question.
        chunks: List of retrieved chunks.

    Returns:
        str: The formatted user message.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}]\n"
            f"Scheme: {chunk['scheme_name']}\n"
            f"URL: {chunk['source_url']}\n"
            f"Content: {chunk['text']}\n"
        )

    context = "\n".join(context_parts)

    return (
        f"User Question: {question}\n\n"
        f"Source Context:\n{context}\n\n"
        f"Answer the user's question using only the source context above."
    )


def call_groq(question, chunks):
    """Call Groq API to generate an answer.

    Args:
        question: The user's question.
        chunks: List of retrieved chunks.

    Returns:
        str: The generated answer.

    Raises:
        ValueError: If Groq configuration is missing.
        Exception: If the API call fails.
    """
    validate_config()

    try:
        from groq import Groq
    except ImportError:
        raise ImportError(
            "groq package is not installed. Run: pip install groq"
        )

    client = Groq(api_key=GROQ_API_KEY)

    system_prompt = build_system_prompt()
    user_message = build_user_message(question, chunks)

    response = client.chat.completions.create(
    model=GROQ_MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ],
    temperature=0.1,
    max_tokens=1000,
)

    return response.choices[0].message.content.strip()
