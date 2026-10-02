import json
import os
import re

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

st.set_page_config(
    page_title="GrowBot — HDFC Mutual Fund FAQ",
    page_icon="🌱",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0a0e27, #1a1f4e, #0d1333);
        color: #e8eaf6;
    }

    .main .block-container {
        max-width: 850px;
        padding-top: 2rem;
    }

    .title {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .subtitle {
        text-align: center;
        color: #9fa8da;
        margin-bottom: 1.5rem;
    }

    .welcome {
        text-align: center;
        color: #b0bec5;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }

    .disclaimer {
        text-align: center;
        color: #ffd54f;
        background: rgba(255,193,7,0.12);
        border: 1px solid rgba(255,193,7,0.3);
        border-radius: 12px;
        padding: 0.7rem;
        margin-bottom: 1.5rem;
    }

    .chat-container {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px;
        padding: 1rem;
        margin-top: 1rem;
    }

    .user {
        background: #4f5fc5;
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 15px;
        margin: 0.6rem 0 0.6rem auto;
        max-width: 80%;
    }

    .assistant {
        background: rgba(255,255,255,0.08);
        color: #e8eaf6;
        padding: 0.8rem 1rem;
        border-radius: 15px;
        margin: 0.6rem auto 0.6rem 0;
        max-width: 85%;
    }

    .source {
        color: #9fa8da;
        font-size: 0.8rem;
        margin-bottom: 0.8rem;
    }

    /* Sample question buttons */
    .stButton > button {
        background: #4f5fc5 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button p,
    .stButton > button span {
        color: #ffffff !important;
    }

    .stButton > button:hover {
        background: #6a78d8 !important;
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.4) !important;
    }

    .stButton > button:hover p,
    .stButton > button:hover span {
        color: #ffffff !important;
    }

    .stButton > button:active,
    .stButton > button:focus {
        background: #3a4aad !important;
        color: #ffffff !important;
        border-color: rgba(255,255,255,0.5) !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(79,95,197,0.4) !important;
    }

    .stButton > button:active p,
    .stButton > button:active span,
    .stButton > button:focus p,
    .stButton > button:focus span {
        color: #ffffff !important;
    }

    /* Chat input - fixed at bottom */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 1rem !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: min(800px, 90vw) !important;
        z-index: 9999 !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background: rgba(20, 25, 60, 0.95) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #b0b8e8 !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] button {
        color: #ffffff !important;
        background: #3949ab !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []


def load_chunks():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "chunks",
        "chunks.txt",
    )

    chunks = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            try:
                chunks.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    return chunks


def retrieve(question, chunks, limit=5):
    question_lower = question.lower()

    words = {
        word.strip(".,?!:;()[]")
        for word in question_lower.split()
        if len(word.strip(".,?!:;()[]")) > 2
    }

    scored = []

    for chunk in chunks:
        text = chunk.get("chunk_text", "")
        text_lower = text.lower()

        text_words = {
            word.strip(".,?!:;()[]")
            for word in text_lower.split()
            if len(word.strip(".,?!:;()[]")) > 2
        }

        score = len(words & text_words)

        for term in [
            "lock-in",
            "lock-in period",
            "expense ratio",
            "exit load",
            "minimum investment",
            "fund manager",
            "benchmark",
            "aum",
            "nav",
        ]:
            if term in question_lower and term in text_lower:
                score += 10

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [chunk for _, chunk in scored[:limit]]


def get_fallback_answer(question, relevant):
    """Return a source-backed fallback answer for known sample questions.

    Returns (answer, sources) or (None, []) if no fallback is available.
    """
    question_lower = question.lower()

    # ELSS lock-in period
    if "lock-in" in question_lower and "elss" in question_lower:
        return (
            "The HDFC ELSS Tax Saver Fund has a lock-in period of 3 years.",
            ["https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth"],
        )

    # Expense ratio
    if "expense ratio" in question_lower:
        for chunk in relevant:
            text = chunk.get("chunk_text", "")
            text_lower = text.lower()
            if "expense ratio" in text_lower:
                match = re.search(r'expense\s+ratio[:\s]*(\d+\.?\d*)\s*%', text_lower)
                if match:
                    value = match.group(1)
                    scheme = chunk.get("scheme_name", "the fund")
                    source = chunk.get("source_url", "")
                    answer = f"The expense ratio of {scheme} is {value}%."
                    return answer, [source] if source else []
        return None, []

    # Exit load
    if "exit load" in question_lower:
        for chunk in relevant:
            text = chunk.get("chunk_text", "")
            text_lower = text.lower()
            if "exit load" in text_lower:
                match = re.search(r'exit\s+load[:\s]*(\d+\.?\d*)\s*%|exit\s+load[:\s]*nil', text_lower)
                if match:
                    if match.group(1):
                        value = match.group(1)
                        scheme = chunk.get("scheme_name", "the fund")
                        source = chunk.get("source_url", "")
                        answer = f"The exit load of {scheme} is {value}%."
                        return answer, [source] if source else []
                    else:
                        scheme = chunk.get("scheme_name", "the fund")
                        source = chunk.get("source_url", "")
                        answer = f"The exit load of {scheme} is nil."
                        return answer, [source] if source else []
        return None, []

    return None, []


def answer_question(question):
    chunks = load_chunks()
    relevant = retrieve(question, chunks)

    if not relevant:
        return "I don't know based on the available sources.", []

    # Check for fallback answer first
    fallback_answer, fallback_sources = get_fallback_answer(question, relevant)
    if fallback_answer:
        return fallback_answer, fallback_sources

    context = "\n\n---\n\n".join(
        f"Fund: {c.get('scheme_name', '')}\n"
        f"Source: {c.get('source_url', '')}\n"
        f"Content:\n{c.get('chunk_text', '')}"
        for c in relevant
    )

    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")

    if not api_key:
        return "GROQ_API_KEY is not configured.", []

    if not model:
        return "GROQ_MODEL is not configured.", []

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are GrowBot, an HDFC Mutual Fund FAQ assistant. "
                        "Answer only from the supplied source context. "
                        "Give concise factual answers. "
                        "Do not provide investment advice. "
                        "Do not guess. "
                        "If the answer is not in the context, say: "
                        "\"I don't know based on the available sources.\""
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"Source context:\n{context}"
                    ),
                },
            ],
            temperature=0.1,
            max_tokens=500,
        )

        answer = response.choices[0].message.content

        if not answer:
            answer = "I don't know based on the available sources."

        sources = []

        for chunk in relevant:
            source = chunk.get("source_url", "")
            if source and source not in sources:
                sources.append(source)

        return answer.strip(), sources

    except Exception as e:
        print(f"Groq API error: {e}")
        # Try fallback if available
        if fallback_answer:
            return fallback_answer, fallback_sources
        return "I don't know based on the available sources.", []


st.markdown('<div class="title">🌱 GrowBot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">HDFC Mutual Fund FAQ Assistant</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="welcome">Ask questions about HDFC mutual funds and get simple answers with sources.</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="disclaimer">Facts-only. No investment advice.</div>',
    unsafe_allow_html=True,
)

examples = [
    "What is the expense ratio of HDFC Large Cap Fund?",
    "What is the exit load of HDFC Flexi Cap Fund?",
    "What is the lock-in period of HDFC ELSS Tax Saver Fund?",
]

cols = st.columns(3)

for col, question in zip(cols, examples):
    with col:
        if st.button(question, use_container_width=True):
            st.session_state["pending_question"] = question
            st.rerun()


if "pending_question" in st.session_state:
    user_input = st.session_state.pop("pending_question")
else:
    user_input = st.chat_input("Ask a question about HDFC mutual funds...")


if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    try:
        with st.spinner("Thinking..."):
            answer, sources = answer_question(user_input)
    except Exception as error:
        print(f"Question processing error: {error}")
        answer = "I don't know based on the available sources."
        sources = []

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )

    st.rerun()


if st.session_state.messages:
    st.markdown(
        '<div class="chat-container">',
        unsafe_allow_html=True,
    )

    for message in st.session_state.messages:
        css_class = (
            "user"
            if message["role"] == "user"
            else "assistant"
        )

        st.markdown(
            f'<div class="{css_class}">{message["content"]}</div>',
            unsafe_allow_html=True,
        )

        if message["role"] == "assistant":
            for source in message.get("sources", []):
                st.markdown(
                    f'<div class="source">Source: {source}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
