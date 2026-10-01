"""Phase 5: Query pipeline — embed, retrieve, guardrail check, and answer."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from query.embedder import embed_question
from query.retriever import retrieve_chunks, get_similarity_scores, filter_chunks
from query.guardrails import check_guardrails
from query.llm import call_groq


def answer_question(question, top_k=10, verbose=False):
    """Process a user question and return an answer.

    This is the main entry point for the query pipeline. It:
    1. Checks guardrails (PII, opinion, off-topic)
    2. Embeds the question
    3. Retrieves relevant chunks from ChromaDB
    4. Checks relevance of retrieved chunks
    5. Calls Groq to generate an answer (if all checks pass)

    Args:
        question: The user's question string.
        top_k: Number of chunks to retrieve (default: 5).
        verbose: If True, print intermediate steps.

    Returns:
        dict: Result with keys:
            - 'answer': The final answer or refusal message.
            - 'sources': List of source URLs (empty if guardrail refused).
            - 'guardrail_triggered': True if a guardrail refused the question.
            - 'reason': Reason for guardrail refusal (None if allowed).
    """
    # Step 1: Pre-retrieval guardrails (PII, opinion, off-topic)
    if verbose:
        print("Checking guardrails...")

    pre_check = check_guardrails(question)
    if not pre_check["allowed"]:
        if verbose:
            print(f"Guardrail triggered: {pre_check['reason']}")
        return {
            "answer": pre_check["response"],
            "sources": [],
            "guardrail_triggered": True,
            "reason": pre_check["reason"],
        }

    # Step 2: Embed the question
    if verbose:
        print("Embedding question...")
    question_embedding = embed_question(question)

    # Step 3: Retrieve chunks
    if verbose:
        print(f"Retrieving top {top_k} chunks...")
    chunks = retrieve_chunks(question_embedding, top_k=top_k)

    # Step 3b: Filter out navigation noise
    original_count = len(chunks)
    chunks = filter_chunks(chunks)
    if verbose:
        print(f"Retrieved {original_count} chunks, {len(chunks)} after filtering navigation noise")
        for i, chunk in enumerate(chunks, 1):
            print(f"  [{i}] {chunk['scheme_name']} (similarity: {chunk['similarity']:.3f})")

    # Step 4: Relevance check
    similarities = get_similarity_scores(chunks)
    post_check = check_guardrails(question, similarities=similarities)
    if not post_check["allowed"]:
        if verbose:
            print(f"Relevance guardrail triggered: {post_check['reason']}")
        return {
            "answer": post_check["response"],
            "sources": [],
            "guardrail_triggered": True,
            "reason": post_check["reason"],
        }

    # Step 5: Call Groq
    if verbose:
        print("Calling Groq API...")
    answer = call_groq(question, chunks)

    # Extract source URLs
    sources = list(set(chunk["source_url"] for chunk in chunks))

    return {
        "answer": answer,
        "sources": sources,
        "guardrail_triggered": False,
        "reason": None,
    }
