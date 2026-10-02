"""Phase 6: Streamlit UI for the HDFC Mutual Fund FAQ Assistant.

Dark navy/indigo starry theme with glass-style chat container.
"""

import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


st.set_page_config(
    page_title="GrowBot — HDFC Mutual Fund FAQ",
    page_icon="",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp,
    .stApp > div,
    .stApp > div > div,
    .main,
    .main .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stHeader"] > div,
    [data-testid="stHeader"] > div > div,
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottom"] > div > div,
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    [data-testid="stChatInput"] form,
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] input,
    [data-testid="stChatInput"] button,
    [data-testid="stButton"] > button,
    [data-testid="stMarkdown"],
    [data-testid="stMarkdownContainer"],
    [data-testid="stSpinner"],
    [data-testid="stChatMessage"],
    [data-testid="stChatMessage"] > div,
    [data-testid="stChatMessage"] > div > div {
        background: transparent !important;
        background-color: transparent !important;
        color: #e8eaf6 !important;
        border-color: transparent !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f4e 50%, #0d1333 100%) !important;
        background-attachment: fixed !important;
        color: #e8eaf6 !important;
        font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    }

    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image:
            radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 40% 70%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1.5px 1.5px at 60% 20%, rgba(255,255,255,0.9), transparent),
            radial-gradient(1px 1px at 80% 50%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1.5px 1.5px at 10% 80%, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 90% 10%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1px 1px at 50% 90%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1.5px 1.5px at 70% 60%, rgba(255,255,255,0.9), transparent),
            radial-gradient(1px 1px at 30% 50%, rgba(255,255,255,0.5), transparent),
            radial-gradient(1px 1px at 85% 85%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1.5px 1.5px at 15% 15%, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 95% 40%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1px 1px at 5% 60%, rgba(255,255,255,0.5), transparent),
            radial-gradient(1.5px 1.5px at 45% 45%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1px 1px at 75% 75%, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 25% 85%, rgba(255,255,255,0.6), transparent),
            radial-gradient(1.5px 1.5px at 55% 5%, rgba(255,255,255,0.7), transparent),
            radial-gradient(1px 1px at 65% 35%, rgba(255,255,255,0.5), transparent),
            radial-gradient(1px 1px at 35% 25%, rgba(255,255,255,0.8), transparent);
        background-repeat: repeat;
        background-size: 100% 100%;
        pointer-events: none;
        z-index: 0;
    }

    .main .block-container {
        position: relative;
        z-index: 1;
        max-width: 800px;
        padding: 2rem 1rem;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .header-title .leaf {
        display: inline-block;
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #4caf50, #81c784);
        border-radius: 0 50% 50% 50%;
        transform: rotate(45deg);
        box-shadow: 0 0 12px rgba(76, 175, 80, 0.6);
    }

    .header-subtitle {
        font-size: 1rem;
        color: #9fa8da;
        text-align: center;
        margin-top: 0.5rem;
    }

    .welcome-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .welcome-text {
        font-size: 1rem;
        color: #b0bec5;
        text-align: center;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }

    .stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e8eaf6 !important;
        padding: 0.75rem !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

    .chat-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        backdrop-filter: blur(10px);
        min-height: 300px;
    }

    .chat-bubble-user {
        background: linear-gradient(135deg, #3949ab, #5c6bc0) !important;
        color: #ffffff !important;
        border-radius: 18px 18px 4px 18px;
        padding: 0.75rem 1.25rem;
        margin: 0.5rem 0 0.5rem auto;
        max-width: 80%;
        display: block;
        box-shadow: 0 2px 8px rgba(57, 73, 171, 0.3);
    }

    .chat-bubble-assistant {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #e8eaf6 !important;
        border-radius: 18px 18px 18px 4px;
        padding: 0.75rem 1.25rem;
        margin: 0.5rem auto 0.5rem 0;
        max-width: 85%;
        display: block;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stChatInput textarea,
    .stChatInput input {
        border-radius: 25px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        padding: 0.75rem 1.25rem !important;
    }

    .stChatInput textarea::placeholder,
    .stChatInput input::placeholder {
        color: #7986cb !important;
    }

    .disclaimer {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.15), rgba(255, 152, 0, 0.1));
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 12px;
        padding: 0.75rem 1.25rem;
        margin: 1rem 0;
        text-align: center;
        color: #ffd54f;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .sources-box {
        background: rgba(255, 255, 255, 0.03);
        border-left: 3px solid #5c6bc0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }

    .sources-box a {
        color: #7986cb;
        text-decoration: none;
    }

    .sources-box a:hover {
        color: #9fa8da;
        text-decoration: underline;
    }

    .clear-btn > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        color: #e8eaf6 !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1rem !important;
    }

    .clear-btn > button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    @media (max-width: 768px) {
        .header-title { font-size: 1.75rem; }
        .welcome-title { font-size: 1.5rem; }
        .chat-bubble-user { max-width: 90%; }
        .chat-bubble-assistant { max-width: 95%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_header():
    st.markdown(
        """
        <div class="header-title">
            <span class="leaf"></span>
            GrowBot
        </div>
        <div class="header-subtitle">HDFC Mutual Fund FAQ Assistant</div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome():
    st.markdown(
        """
        <div class="welcome-title">Hi! I'm GrowBot</div>
        <div class="welcome-text">
            Ask me anything about HDFC mutual funds — I'll give you accurate,
            easy-to-understand answers with sources.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_disclaimer():
    st.markdown(
        """
        <div class="disclaimer">
            Facts-only. No investment advice.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_example_questions():
    st.markdown(
        "<p style='color: #9fa8da; text-align: center; margin-bottom: 0.5rem;'>Try asking:</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    examples = [
        "What is the expense ratio of HDFC Large Cap Fund?",
        "What is the exit load of HDFC Flexi Cap Fund?",
        "What is the lock-in period of HDFC ELSS Tax Saver Fund?",
    ]

    for col, question in zip([col1, col2, col3], examples):
        with col:
            if st.button(
                question,
                key=f"example_{question}",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state["pending_question"] = question
                st.rerun()


def render_chat_history():
    if not st.session_state.messages:
        return

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f'<div class="chat-bubble-user">{message["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-bubble-assistant">{message["content"]}</div>',
                unsafe_allow_html=True,
            )
            if message.get("sources"):
                source_links = "".join(
                    f'<a href="{source}" target="_blank">{source}</a><br>'
                    for source in message["sources"]
                )
                st.markdown(
                    f'<div class="sources-box"><strong>Sources:</strong><br>{source_links}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)


def render_clear_button():
    if st.session_state.messages:
        st.markdown(
            """
            <style>
            .clear-btn { position: fixed; top: 1rem; right: 1rem; z-index: 100; }
            </style>
            """,
            unsafe_allow_html=True,
        )
        with st.container():
            col1, col2, col3 = st.columns([1, 1, 1])
            with col3:
                if st.button("Clear Chat", type="secondary", use_container_width=True):
                    st.session_state.messages = []
                    st.rerun()


def process_question(question):
    from query.pipeline import answer_question

    with st.spinner("Thinking..."):
        result = answer_question(question, top_k=10, verbose=False)
    return result["answer"], result["sources"]


def main():
    render_clear_button()
    render_header()
    render_welcome()
    render_disclaimer()
    render_example_questions()

    user_input = st.chat_input("Ask a question about HDFC mutual funds...")

    if "pending_question" in st.session_state:
        user_input = st.session_state.pop("pending_question")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        answer, sources = process_question(user_input)
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
        })
        st.rerun()

    render_chat_history()


if __name__ == "__main__":
    main()
