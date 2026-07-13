"""
streamlit_app.py

Streamlit UI for the Legal RAG System.
Deploy this on Streamlit Community Cloud (1GB free RAM - enough for the
FULL hybrid system: Vector Search + BM25 + Groq LLM, no simplification needed).

IMPORTANT SETUP STEPS:
1. This file goes in your project ROOT (same level as the "python" folder).
2. Your GROQ_API_KEY must be added as a Streamlit secret (NOT just in .env):
   - On Streamlit Community Cloud: App Settings -> Secrets -> add:
       GROQ_API_KEY = "your-key-here"
   - Locally for testing: create a file .streamlit/secrets.toml with the same line.
3. Your GitHub repo must be PUBLIC for the free Community Cloud tier.
4. requirements.txt must include "streamlit" in addition to your existing packages.
"""

import os
import streamlit as st

# ------------------------------------------------------------
# Push Streamlit secret into the environment BEFORE importing
# llm_answer, since llm_answer.py reads GROQ_API_KEY via os.getenv().
# This means you don't have to change your existing llm_answer.py at all.
# ------------------------------------------------------------
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

from python.llm_answer import ask  # noqa: E402  (import after env var is set)

# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="Legal RAG System",
    page_icon="⚖️",
    layout="centered",
)

st.title("⚖️ Legal RAG System")
st.caption("US Tax & Legal Domain — ask a question and get a cited answer from the document database.")

# ==============================
# SESSION STATE (keeps chat history during the session)
# ==============================

if "history" not in st.session_state:
    st.session_state.history = []

# ==============================
# INPUT
# ==============================

query = st.text_input(
    "Ask a legal or tax question:",
    placeholder="e.g. What does the Fair Labor Standards Act say about overtime pay?",
)

col1, col2 = st.columns([1, 5])
with col1:
    submit = st.button("Ask", type="primary")

if submit and query.strip():
    with st.spinner("Searching documents and generating answer..."):
        try:
            result = ask(query.strip())
        except Exception as e:
            result = {"success": False, "answer": f"Error: {e}", "sources": []}

    st.session_state.history.insert(0, {"query": query.strip(), "result": result})

# ==============================
# DISPLAY RESULTS (most recent first)
# ==============================

for entry in st.session_state.history:
    st.markdown("---")
    st.markdown(f"**Q: {entry['query']}**")

    result = entry["result"]

    if not result.get("success"):
        st.error(result.get("answer", "Something went wrong."))
    else:
        st.markdown(result["answer"])

        sources = result.get("sources", [])
        if sources:
            with st.expander(f"📄 Retrieved Sources ({len(sources)})"):
                for i, s in enumerate(sources, start=1):
                    doc = s.get("document", s.get("filename", "unknown"))
                    doc_type = s.get("doc_type", "")
                    pages = f"{s.get('page_start', '?')}-{s.get('page_end', '?')}"
                    score = s.get("score", "")
                    st.write(f"**[{i}]** {doc}  ·  *{doc_type}*  ·  Pages {pages}  ·  Score: {score}")

if not st.session_state.history:
    st.info("Ask a question above to get started. Answers are grounded in the 100-document legal/tax corpus, with citations.")