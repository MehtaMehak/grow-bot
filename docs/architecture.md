# Architecture Document
## Mutual Fund FAQ Assistant (Facts-Only Q&A)

---

## 1. System Components

| # | Component | Technology |
|---|-----------|------------|
| 1 | Document Loader | Python (file/URL readers) |
| 2 | Chunker | Python (text splitting logic) |
| 3 | Embedding Engine | sentence-transformers/all-MiniLM-L6-v2 |
| 4 | Vector Database | ChromaDB (persistent) |
| 5 | LLM | Groq API |
| 6 | UI | Streamlit |

---

## 2. Responsibilities of Each Component

### Document Loader
- Reads source documents (public sources about HDFC mutual fund schemes).
- Outputs raw text for chunking.

### Chunker
- Splits raw text into smaller, meaningful chunks.
- Each chunk is small enough to be relevant but large enough to retain context.

### Embedding Engine
- Converts text chunks into numerical vectors using all-MiniLM-L6-v2.
- The same model is used for both document chunks and user questions (ensures vector space alignment).

### Vector Database (ChromaDB)
- Stores all document chunk embeddings persistently on disk.
- Survives application restarts (no re-ingestion needed unless sources change).
- Supports similarity search to find the most relevant chunks for a given query.

### LLM (Groq)
- Receives the user question + retrieved context chunks.
- Generates a concise, facts-only answer (max 3 sentences) with a source link.
- Refuses opinion-based questions with a polite facts-only response.

### UI (Streamlit)
- Displays welcome message, 3 example questions, and "Facts-only. No investment advice." note.
- Accepts user questions and displays answers.

---

## 3. End-to-End Data Flow

### Ingestion Flow (runs once or when sources change)

```
┌─────────────┐     ┌─────────┐     ┌──────────────┐     ┌────────────────┐
│   Load      │────▶│  Chunk  │────▶│    Embed     │────▶│  Store in      │
│  Documents  │     │  Text   │     │  (MiniLM)    │     │  Vector DB     │
└─────────────┘     └─────────┘     └──────────────┘     │  (ChromaDB)    │
                                                         └────────────────┘
```

**Steps:**
1. **Load** — Read source documents (public sources about HDFC schemes).
2. **Chunk** — Split documents into smaller text chunks.
3. **Embed** — Convert each chunk to a vector using all-MiniLM-L6-v2.
4. **Store** — Save vectors + chunk text in ChromaDB (persistent on disk).

---

### Query Flow (runs every time the user asks a question)

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐     ┌─────────┐     ┌──────────┐
│  Question   │────▶│    Embed     │────▶│  Retrieve top  │────▶│   LLM   │────▶│  Answer  │
│  from User  │     │  (MiniLM)    │     │  chunks (DB)   │     │ (Groq)  │     │  to User │
└─────────────┘     └──────────────┘     └────────────────┘     └─────────┘     └──────────┘
```

**Steps:**
1. **Question** — User types a question in the Streamlit UI.
2. **Embed** — Convert the question to a vector using the same all-MiniLM-L6-v2 model.
3. **Retrieve** — Search ChromaDB for the most similar chunks (top-k).
4. **LLM** — Send question + retrieved chunks to Groq; get a facts-only answer.
5. **Answer** — Display the answer (max 3 sentences, with source link) in the UI.

---

## 4. Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector DB | ChromaDB (persistent) |
| LLM | Groq API |
| UI | Streamlit |
| Secrets | .env (Groq API key, never committed to Git) |

---

## 5. Folder Structure

```
grow_bot/
├── .env                          # Groq API key (never committed)
├── .gitignore                    # Ignores .env, vector_db/, __pycache__/
├── ProblemStatement.txt
├── docs/
│   ├── PRD.md
│   └── architecture.md
├── data/
│   └── sources/                  # Public source documents (text/PDF)
├── vector_db/                    # ChromaDB persistent storage (auto-created)
├── ingestion/
│   ├── loader.py                 # Load documents
│   ├── chunker.py                # Split into chunks
│   ├── embedder.py               # Embed chunks with MiniLM
│   └── store.py                  # Store in ChromaDB
├── query/
│   ├── embedder.py               # Embed user question (same model)
│   ├── retriever.py              # Retrieve top chunks from ChromaDB
│   └── llm.py                    # Call Groq, generate answer
├── app.py                        # Streamlit UI
└── requirements.txt
```

---

## 6. Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                        INGESTION PIPELINE                           ║
║                                                                      ║
║  [Source Docs] ──▶ [Loader] ──▶ [Chunker] ──▶ [Embedder] ──▶ [ChromaDB] ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ (persistent storage on disk)
                                    ▼
╔══════════════════════════════════════════════════════════════════════╗
║                         QUERY PIPELINE                              ║
║                                                                      ║
║  [User Question] ──▶ [Embedder] ──▶ [Retriever] ──▶ [Groq LLM] ──▶ [Answer] ║
║       ▲            (same model)      (ChromaDB)                      ║
║       │                                                              ║
║  [Streamlit UI]                                                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 7. How Ingestion and Query Flows Connect

The two flows are connected through the **ChromaDB persistent vector database**:

1. **Ingestion** populates the vector database with embedded document chunks. This happens once (or when source documents change).
2. **Query** reads from the same vector database to find relevant context for each user question.
3. The **same embedding model** (all-MiniLM-L6-v2) is used in both flows, ensuring that document chunks and user questions live in the same vector space — this is what makes similarity search work.
4. Because ChromaDB is **persistent**, the ingestion results survive restarts. The query flow can immediately use the stored vectors without re-ingesting.

**In short:** Ingestion builds the knowledge base; Query uses it to answer questions.

---

*End of Architecture Document*
