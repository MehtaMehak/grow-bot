# Implementation Plan
## Mutual Fund FAQ Assistant (Facts-Only Q&A)

---

## Overview

This plan divides the implementation into 6 phases, following the architecture
and PRD. Each phase builds on the previous one. No code is written yet — this is
only the plan.

---

## Phase 1 — Project Setup

### Goal
Set up the project structure, dependencies, and environment configuration.

### Files to Create/Modify

| File | Purpose |
|------|---------|
| `requirements.txt` | Lists all Python dependencies (sentence-transformers, chromadb, groq, streamlit, python-dotenv) |
| `.env` | Stores the Groq API key (never committed to Git) |
| `.gitignore` | Ignores `.env`, `vector_db/`, `__pycache__/`, and other non-source files |
| `data/sources/` | Directory to store public source documents about HDFC schemes |

### Main Implementation Tasks
1. Create the folder structure as defined in the architecture document.
2. Create `requirements.txt` with all required packages.
3. Create `.env` with a placeholder for the Groq API key.
4. Create `.gitignore` to exclude `.env`, `vector_db/`, and `__pycache__/`.
5. Create the `data/sources/` directory for source documents.

### How to Verify/Test
- Run `pip install -r requirements.txt` — all packages install without errors.
- Confirm `.env` exists and is listed in `.gitignore`.
- Confirm the folder structure matches the architecture document.

---

## Phase 2 — Loading & Chunking

### Goal
Load public source documents about HDFC mutual fund schemes and split them into
smaller text chunks suitable for embedding.

### Files to Create/Modify

| File | Purpose |
|------|---------|
| `ingestion/loader.py` | Loads source documents (text/PDF) from `data/sources/` and returns raw text |
| `ingestion/chunker.py` | Splits raw text into smaller chunks with configurable chunk size and overlap |

### Main Implementation Tasks
1. Implement `loader.py` to read files from `data/sources/` and extract text.
2. Implement `chunker.py` to split text into chunks (e.g., 500 characters with 50-character overlap).
3. Ensure each chunk retains enough context to be meaningful on its own.
4. Store source link metadata alongside each chunk (needed for citation in answers).

### How to Verify/Test
- Place a sample source document in `data/sources/`.
- Run the loader and confirm it reads the file and outputs raw text.
- Run the chunker and confirm the text is split into chunks of the expected size.
- Confirm each chunk has an associated source link.

---

## Phase 3 — Embedding & Vector Store

### Goal
Convert text chunks into numerical vectors using all-MiniLM-L6-v2 and store them
in ChromaDB for persistent similarity search.

### Files to Create/Modify

| File | Purpose |
|------|---------|
| `ingestion/embedder.py` | Loads the all-MiniLM-L6-v2 model and converts text chunks into embedding vectors |
| `ingestion/store.py` | Stores embeddings + chunk text + source links in ChromaDB (persistent) |

### Main Implementation Tasks
1. Implement `embedder.py` to load `sentence-transformers/all-MiniLM-L6-v2` and encode text into vectors.
2. Implement `store.py` to create/load a persistent ChromaDB collection.
3. Store each chunk's vector, text, and source link in ChromaDB.
4. Ensure the ChromaDB directory (`vector_db/`) persists between runs.
5. Add a check: if the collection already has data, skip re-ingestion.

### How to Verify/Test
- Run the ingestion pipeline on sample documents.
- Confirm `vector_db/` directory is created and populated.
- Run the pipeline again and confirm it does NOT duplicate data (persistence check).
- Query ChromaDB directly to confirm vectors and metadata are stored correctly.

---

## Phase 4 — Guardrails

### Goal
Implement the facts-only guardrails that prevent the assistant from giving
investment advice, making up answers, or producing performance claims.

### Files to Create/Modify

| File | Purpose |
|------|---------|
| `query/guardrails.py` | Contains logic to detect opinion-based questions and enforce facts-only responses |

### Main Implementation Tasks
1. Implement a function to detect opinion-based questions (e.g., "should I buy", "should I sell", "is it good to invest").
2. Implement a function to detect when retrieved chunks are not relevant enough (low similarity score).
3. Implement response templates:
   - Opinion-based refusal: polite facts-only message + educational source link.
   - No-answer-found: "I don't know" message.
4. Ensure no performance claims or return calculations can appear in responses.

### How to Verify/Test
- Test with opinion-based questions (e.g., "Should I buy HDFC Small Cap Fund?") — confirm the response is a polite refusal with an educational link.
- Test with questions that have no answer in sources — confirm the response says "I don't know."
- Test with factual questions — confirm the response is a normal sourced answer.
- Confirm no response contains performance claims or return calculations.

---

## Phase 5 — Retrieval + LLM Answer

### Goal
Embed the user's question, retrieve the most relevant chunks from ChromaDB, and
generate a concise facts-only answer using Groq.

### Files to Create/Modify

| File | Purpose |
|------|---------|
| `query/embedder.py` | Embeds the user question using the same all-MiniLM-L6-v2 model |
| `query/retriever.py` | Retrieves top-k most similar chunks from ChromaDB |
| `query/llm.py` | Sends question + retrieved chunks to Groq and formats the answer |

### Main Implementation Tasks
1. Implement `query/embedder.py` to encode the user question using the same model as ingestion.
2. Implement `retriever.py` to query ChromaDB and return the top-k most similar chunks.
3. Implement `llm.py` to:
   - Build a system prompt with facts-only instructions (max 3 sentences, include source link, include "Last updated from sources:").
   - Send the user question + retrieved chunks to Groq.
   - Return the formatted answer.
4. Integrate guardrails (Phase 4) into the query flow: check for opinion-based questions and low-relevance retrievals before calling the LLM.

### How to Verify/Test
- Test with a factual question (e.g., "What is the expense ratio?") — confirm the answer is max 3 sentences, includes a source link, and includes "Last updated from sources:".
- Test with an opinion-based question — confirm the guardrail triggers and the LLM is not called.
- Test with a question that has no relevant chunks — confirm the "I don't know" response is returned.
- Confirm the same embedding model is used in both `ingestion/embedder.py` and `query/embedder.py`.

---

## Phase 6 — UI

### Goal
Build the Streamlit UI with a welcome message, 3 example questions, and the
"Facts-only. No investment advice." note.

### Files to Create/Modify

| File | Purpose |
|------|---------|
| `app.py` | Streamlit application — welcome message, example questions, chat input, answer display |

### Main Implementation Tasks
1. Set up the Streamlit app with a title and welcome message.
2. Display 3 example questions as clickable suggestions.
3. Display the note: "Facts-only. No investment advice."
4. Add a text input for the user's question.
5. Connect the input to the query pipeline (Phases 4 + 5).
6. Display the answer (with source link) in the UI.
7. Ensure no PII is collected or displayed.

### How to Verify/Test
- Run `streamlit run app.py` — the app loads without errors.
- Confirm the welcome message, 3 example questions, and "Facts-only. No investment advice." note are displayed.
- Click an example question — confirm it triggers the query pipeline and displays an answer.
- Type a factual question — confirm the answer appears with a source link.
- Type an opinion-based question — confirm the polite refusal appears.
- Confirm no PII fields exist in the UI.

---

## Summary of Phases

| Phase | Name | What It Delivers |
|-------|------|------------------|
| 1 | Project Setup | Folder structure, dependencies, .env, .gitignore |
| 2 | Loading & Chunking | Load source documents, split into chunks with source links |
| 3 | Embedding & Vector Store | Embed chunks with all-MiniLM-L6-v2, store in persistent ChromaDB |
| 4 | Guardrails | Detect opinion-based questions, enforce facts-only responses |
| 5 | Retrieval + LLM Answer | Embed question, retrieve chunks, generate sourced answer via Groq |
| 6 | UI | Streamlit app with welcome message, examples, and disclaimer |

---

*End of Implementation Plan*
