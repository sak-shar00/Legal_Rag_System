"""
llm_answer.py
Legal RAG - Milestone 3
Hybrid Search + Groq LLM
"""

import os
import pickle
import faiss
import numpy as np

from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from .config import (
    MODEL_NAME,
    TOP_K_VECTOR,
    TOP_K_BM25,
    VECTOR_WEIGHT,
    BM25_WEIGHT,
)

from .preprocess import preprocess
from .utils import (
    normalize_scores,
    hybrid_score,
    sort_results,
    remove_duplicates,
)


# ============================================================
# LOAD ENV
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

client = Groq(api_key=API_KEY)

TOP_CHUNKS_FOR_LLM = 8

print("=" * 70)
print("Groq Connected Successfully")
print("=" * 70)

# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading Embedding Model...")
embed_model = SentenceTransformer(MODEL_NAME)

# ============================================================
# LOAD FAISS
# ============================================================

print("Loading FAISS Index...")

index_path = os.path.join(BASE_DIR, "faiss.index")
index = faiss.read_index(index_path)

metadata_path = os.path.join(BASE_DIR, "metadata.pkl")
with open(metadata_path, "rb") as f:
    faiss_metadata = pickle.load(f)

# ============================================================
# LOAD BM25
# ============================================================

print("Loading BM25...")

bm25_path = os.path.join(BASE_DIR, "bm25.pkl")
with open(bm25_path, "rb") as f:
    bm25 = pickle.load(f)

bm25_metadata_path = os.path.join(BASE_DIR, "bm25_metadata.pkl")
with open(bm25_metadata_path, "rb") as f:
    bm25_metadata = pickle.load(f)


print("\nSystem Ready!\n")
# ============================================================
# HYBRID RETRIEVAL
# ============================================================

def hybrid_retrieve(query):

    # -------- VECTOR SEARCH --------
    query_embedding = embed_model.encode(
        [query],
        normalize_embeddings=True
    )

    faiss_scores, faiss_ids = index.search(
        query_embedding,
        TOP_K_VECTOR
    )

    vector_scores = normalize_scores(faiss_scores[0])

    # -------- BM25 SEARCH --------

    tokenized_query = preprocess(query)

    bm25_scores = bm25.get_scores(tokenized_query)

    top_bm25_ids = np.argsort(bm25_scores)[::-1][:TOP_K_BM25]

    top_bm25_scores = [
        bm25_scores[i]
        for i in top_bm25_ids
    ]

    bm25_scores_norm = normalize_scores(top_bm25_scores)

    # -------- MERGE BOTH --------

    merged = {}

    for idx, score in zip(faiss_ids[0], vector_scores):

        chunk = faiss_metadata[idx]

        merged[chunk["chunk_id"]] = {
            **chunk,
            "vector_score": float(score),
            "bm25_score": 0.0
        }

    for idx, score in zip(top_bm25_ids, bm25_scores_norm):

        chunk = bm25_metadata[idx]

        if chunk["chunk_id"] in merged:

            merged[chunk["chunk_id"]]["bm25_score"] = float(score)

        else:

            merged[chunk["chunk_id"]] = {
                **chunk,
                "vector_score": 0.0,
                "bm25_score": float(score)
            }

    results = []

    for chunk in merged.values():

        chunk["hybrid_score"] = hybrid_score(
            chunk["vector_score"],
            chunk["bm25_score"],
            VECTOR_WEIGHT,
            BM25_WEIGHT,
        )

        results.append(chunk)

    results = remove_duplicates(results)

    results = [
        r
        for r in results
        if len(r["text"].split()) > 80
    ]

    results = sort_results(results)

    filtered = []

    seen_docs = set()

    for r in results:

        if r["filename"] not in seen_docs:

            filtered.append(r)

            seen_docs.add(r["filename"])

    filtered = [x for x in filtered if x["hybrid_score"] >= 0.25]

    return filtered[:TOP_CHUNKS_FOR_LLM]



# ============================================================
# PROMPT
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