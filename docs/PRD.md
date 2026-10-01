# Product Requirements Document (PRD)
## Mutual Fund FAQ Assistant (Facts-Only Q&A)

---

## 1. Product Goal

Build a small FAQ assistant that answers factual questions about five HDFC mutual fund schemes available on the Groww platform. The assistant provides sourced, factual answers only — never investment advice.

---

## 2. Target Users

- Mutual fund investors on Groww who need quick, accurate, factual information about HDFC schemes.
- Users who want sourced answers (with links) rather than opinions or recommendations.

---

## 3. Problem Being Solved

Investors frequently have factual questions about scheme parameters (expense ratio, exit load, minimum SIP, lock-in periods, riskometer, benchmarks, statement downloads, etc.). They need fast, accurate, sourced answers — not opinions or investment advice. Generic chatbots may hallucinate, give unsourced responses, or cross into advice territory. This product solves that by providing a facts-only, source-cited FAQ assistant.

---

## 4. In-Scope Features

- Answer factual questions about the five HDFC schemes:
  1. HDFC Large Cap Fund
  2. HDFC Flexi Cap Fund
  3. HDFC ELSS Tax Saver Fund
  4. HDFC Small Cap Fund
  5. HDFC Balanced Advantage Fund
- Provide one source link per answer.
- Refuse opinion-based questions (buy/sell/invest) with a polite facts-only response and an educational source link.
- Indicate when an answer is not available in the provided sources (say "I don't know" rather than making up an answer).
- Display a welcome message, 3 example questions, and a "Facts-only. No investment advice." note in the UI.

---

## 5. Out-of-Scope Features

- Investment advice, recommendations, or opinions.
- Performance claims or return calculations.
- Personal financial planning.
- Any data beyond the five listed HDFC schemes.
- Collection or use of PII (PAN, Aadhaar, account numbers, OTPs, email addresses, phone numbers).

---

## 6. Example User Questions

- What is the expense ratio?
- What is the exit load?
- What is the minimum SIP?
- What is the ELSS lock-in period?
- What is the riskometer?
- What is the benchmark?
- How can I download my statement?

---

## 7. Functional Requirements

| # | Requirement |
|---|-------------|
| FR1 | Every answer must include one source link. |
| FR2 | Answers must be a maximum of 3 sentences. |
| FR3 | Answers must include "Last updated from sources:" with the retrieval date. |
| FR4 | Do not make performance claims or calculate returns. |
| FR5 | Use public sources only. |
| FR6 | Do not collect or use PII such as PAN, Aadhaar, account numbers, OTPs, email addresses, or phone numbers. |
| FR7 | If the answer is not available in the provided sources, say that you don't know rather than making up an answer. |

---

## 8. Guardrails and Facts-Only Requirements

| # | Guardrail |
|---|-----------|
| G1 | If the user asks whether they should buy, sell, or invest in a fund, do not give investment advice. |
| G2 | Respond with a polite facts-only message and provide an educational source link. |
| G3 | Never fabricate answers — if the information is not in the retrieved sources, state that the answer is not available. |
| G4 | All answers must be grounded in retrieved source chunks from the vector database. |

---

## 9. UI Requirements

| # | Requirement |
|---|-------------|
| UI1 | Display a welcome message on load. |
| UI2 | Show 3 example questions as suggestions. |
| UI3 | Display the note: "Facts-only. No investment advice." |
| UI4 | Built with Streamlit. |

---

## 10. Success Criteria

- The assistant answers factual questions accurately with a source link.
- The assistant refuses opinion-based questions politely with an educational link.
- Answers are concise (max 3 sentences) and include "Last updated from sources:".
- No performance claims or return calculations are ever produced.
- No PII is collected or displayed.
- The application is locally runnable and deployable on Render.

---

## 11. Constraints and Technology Requirements

| # | Constraint |
|---|------------|
| TC1 | Language: Python |
| TC2 | Embeddings: sentence-transformers/all-MiniLM-L6-v2 (local) |
| TC3 | Vector DB: ChromaDB (persistent — must survive restarts) |
| TC4 | LLM: Groq API |
| TC5 | UI: Streamlit |
| TC6 | Same embedding model must be used for document chunks and user questions |
| TC7 | Groq API key must be stored in .env and never committed to Git |
| TC8 | Free-tier friendly |
| TC9 | Locally runnable |
| TC10 | Deployable on Render |

---

## RAG Architecture

**Ingestion:**
```
Load → Chunk → Embed → Store in Vector DB
```

**Query:**
```
Question → Embed → Retrieve top chunks → LLM → Answer
```

---

*End of PRD*
