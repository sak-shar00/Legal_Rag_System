"""
llm_answer.py  (DEPLOYMENT / LIGHTWEIGHT VERSION)
Legal RAG - Milestone 3
BM25-only retrieval + Groq LLM

WHY THIS VERSION EXISTS:
The full hybrid system (Vector + BM25) uses sentence-transformers, which
loads PyTorch and needs 1GB+ RAM to run. Free hosting tiers (Render, Koyeb,
etc.) cap free instances at 512MB, which crashes with the full system.

This version drops the Vector Search component and uses BM25 (keyword
search) only. BM25 needs no ML model, no PyTorch - just the .pkl files -
so it fits comfortably in 512MB.

IMPORTANT: This is a deployment-only simplification. Your evaluation
numbers in the Evaluation Report were measured against the FULL hybrid
system running locally - those results remain valid. This lightweight
version exists only so the LIVE DEMO can run on a free host without
crashing. Document this clearly in your report/demo notes.
"""

import os
import pickle
import numpy as np

from dotenv import load_dotenv
from groq import Groq

from .config import TOP_K_BM25
from .preprocess import preprocess

# ============================================================
# LOAD ENV
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

client = Groq(api_key=API_KEY)

TOP_CHUNKS_FOR_LLM = 5
MIN_RELEVANCE_SCORE = 0.05  # BM25 raw scores aren't 0-1 normalized the same way as hybrid; tune after testing

print("=" * 70)
print("Groq Connected Successfully (Lightweight BM25-only deployment mode)")
print("=" * 70)

# ============================================================
# LOAD BM25 ONLY (no embedding model, no FAISS - keeps memory low)
# ============================================================

print("Loading BM25...")

bm25_path = os.path.join(BASE_DIR, "bm25.pkl")
with open(bm25_path, "rb") as f:
    bm25 = pickle.load(f)

bm25_metadata_path = os.path.join(BASE_DIR, "bm25_metadata.pkl")
with open(bm25_metadata_path, "rb") as f:
    bm25_metadata = pickle.load(f)

print("\nSystem Ready! (BM25-only mode)\n")


# ============================================================
# BM25-ONLY RETRIEVAL
# ============================================================

def normalize_scores(scores):
    scores = np.array(scores, dtype=float)
    if len(scores) == 0:
        return scores
    min_s, max_s = scores.min(), scores.max()
    if max_s == min_s:
        return np.ones(len(scores))
    return (scores - min_s) / (max_s - min_s)


def hybrid_retrieve(query):
    """Same function name as the full version so main.py doesn't need changes."""

    tokenized_query = preprocess(query)
    bm25_scores = bm25.get_scores(tokenized_query)

    top_ids = np.argsort(bm25_scores)[::-1][:TOP_K_BM25]
    top_scores = [bm25_scores[i] for i in top_ids]
    norm_scores = normalize_scores(top_scores)

    results = []
    for idx, score in zip(top_ids, norm_scores):
        chunk = bm25_metadata[idx]
        chunk = {**chunk, "hybrid_score": float(score)}
        results.append(chunk)

    results = [r for r in results if len(r["text"].split()) > 80]
    results = sorted(results, key=lambda x: x["hybrid_score"], reverse=True)

    filtered = []
    seen_docs = set()
    for r in results:
        if r["filename"] not in seen_docs:
            filtered.append(r)
            seen_docs.add(r["filename"])

    filtered = [x for x in filtered if x["hybrid_score"] >= MIN_RELEVANCE_SCORE]

    return filtered[:TOP_CHUNKS_FOR_LLM]


# ============================================================
# PROMPT (identical to your full version)
# ============================================================

def build_prompt(query, chunks):

    context = ""

    for i, chunk in enumerate(chunks, start=1):

        context += f"""
========================
SOURCE {i}

Document Name : {chunk['filename']}
Document Type : {chunk['doc_type']}
Pages         : {chunk['page_start']} - {chunk['page_end']}

Content:
{chunk['text']}
========================
"""

    prompt = f"""
You are an expert US Tax and Legal Research Assistant.

You must answer ONLY using the retrieved legal documents provided below.

STRICT RULES:

1. NEVER use outside knowledge.

2. NEVER guess.

3. If the answer cannot be found in the retrieved documents, respond exactly:

"The retrieved legal documents do not contain sufficient information to answer this question."

4. Every factual statement MUST include a citation.

Citation format:

(Document: filename, Pages: start-end)

5. If multiple documents support the answer,
combine the information and cite all relevant documents.

6. Use clear legal language.

7. Do NOT mention "SOURCE 1", "SOURCE 2".

8. Answer in this exact format:

------------------------------------------------

Answer

<your answer>

Primary Citation

(Document: filename, Pages: x-y)

Additional References

- filename (Pages x-y)
- filename (Pages x-y)

------------------------------------------------

Retrieved Documents

{context}

Question:

{query}
"""
    return prompt


# ============================================================
# LLM CALL
# ============================================================

def generate_answer(prompt):

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": "You are an expert Legal Research Assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,
        max_tokens=1024,
    )

    return response.choices[0].message.content


# ============================================================
# ASK QUESTION
# ============================================================

def ask(query):

    chunks = hybrid_retrieve(query)

    if len(chunks) == 0:
        return {
            "success": False,
            "answer": "No relevant documents found.",
            "sources": []
        }

    prompt = build_prompt(query, chunks)

    try:

        answer = generate_answer(prompt)

        sources = []

        for chunk in chunks:

            sources.append({
                "document": chunk["filename"],
                "doc_type": chunk["doc_type"],
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
                "score": round(chunk["hybrid_score"], 4)
            })

        return {
            "success": True,
            "question": query,
            "answer": answer,
            "sources": sources
        }

    except Exception as e:

        return {
            "success": False,
            "answer": str(e),
            "sources": []
        }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    while True:

        query = input("\nAsk Question : ")

        if query.lower() == "exit":
            break

        result = ask(query)

        print("\n" + "=" * 90)
        print("ANSWER")
        print("=" * 90)
        print(result["answer"])

        print("\n" + "=" * 90)
        print("Retrieved Sources")
        print("=" * 90)

        for i, source in enumerate(result["sources"], start=1):

            print(
                f"[{i}] {source['document']} | "
                f"{source['doc_type']} | "
                f"Pages {source['page_start']}-{source['page_end']} | "
                f"Score: {source['score']}"
            )

        print()