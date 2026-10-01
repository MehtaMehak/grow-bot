"""Phase 5 CLI test script — ask a question from the terminal.

Usage:
    python test_phase5.py
    python test_phase5.py "What is the expense ratio of HDFC Large Cap Fund?"
"""

import os
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from query.pipeline import answer_question


def main():
    print("=" * 70)
    print("PHASE 5 — RETRIEVAL + LLM ANSWER (CLI TEST)")
    print("=" * 70)

    # Get question from command line or prompt
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("\nEnter your question: ").strip()

    if not question:
        print("Error: No question provided.")
        sys.exit(1)

    print(f"\nQuestion: {question}")
    print("-" * 70)

    # Process the question
    result = answer_question(question, top_k=10, verbose=True)

    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    if result["guardrail_triggered"]:
        print(f"\nGuardrail triggered: {result['reason']}")
        print(f"\nResponse:\n{result['answer']}")
    else:
        print(f"\nSources:")
        for source in result["sources"]:
            print(f"  - {source}")

        print(f"\nAnswer:\n{result['answer']}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
