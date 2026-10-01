# GrowBot 🌱

A facts-only Mutual Fund FAQ assistant built as a learning project for my NextLeap Product Management journey.

GrowBot answers factual questions about selected HDFC mutual fund schemes using a Retrieval-Augmented Generation (RAG) pipeline.

## 🎯 What GrowBot Does

Users can ask questions such as:

- What is the expense ratio?
- What is the exit load?
- What is the minimum SIP amount?
- What is the ELSS lock-in period?
- What is the riskometer?
- What is the benchmark?
- How can I download a statement?

Every factual answer includes a source link and:

**"Last updated from sources:"**

GrowBot does not provide investment advice or predict returns.

## 🛡️ Guardrails

GrowBot is designed to stay facts-only.

It refuses:

- Investment recommendations
- Buy/sell questions
- Return predictions
- Off-topic questions
- Questions involving sensitive personal information

Example:

> Should I invest in HDFC Large Cap Fund?

GrowBot responds with a facts-only refusal rather than giving a recommendation.

## 🧠 How It Works

GrowBot uses a Retrieval-Augmented Generation (RAG) architecture:

```text
User Question
     ↓
Question Embedding
     ↓
ChromaDB Retrieval
     ↓
Relevant Source Chunks
     ↓
Groq LLM
     ↓
Facts-only Answer + Source
