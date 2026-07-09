import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from preprocess import preprocess

from config import (
    MODEL_NAME,
    TOP_K_VECTOR,
    TOP_K_BM25,
    FINAL_RESULTS,
    VECTOR_WEIGHT,
    BM25_WEIGHT
)

from utils import (
    normalize_scores,
    hybrid_score,
    sort_results,
    remove_duplicates
)

print("Loading Embedding Model...")
model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS Index...")
index = faiss.read_index("faiss.index")

with open("metadata.pkl", "rb") as f:
    faiss_metadata = pickle.load(f)

print("Loading BM25...")

with open("bm25.pkl", "rb") as f:
    bm25 = pickle.load(f)

with open("bm25_metadata.pkl", "rb") as f:
    bm25_metadata = pickle.load(f)

print("\nHybrid Search Ready!")

while True:

    query = input("\nAsk Question : ")

    if query.lower() == "exit":
        break

    # ==================================================
    # VECTOR SEARCH
    # ==================================================

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    faiss_scores, faiss_ids = index.search(
        query_embedding,
        TOP_K_VECTOR
    )

    vector_scores = normalize_scores(faiss_scores[0])

    # ==================================================
    # BM25 SEARCH
    # ==================================================

       # ==================================================
    # BM25 SEARCH
    # ==================================================

    tokenized_query = preprocess(query)

    bm25_scores = bm25.get_scores(tokenized_query)

    top_bm25_ids = np.argsort(bm25_scores)[::-1][:TOP_K_BM25]

    top_bm25_scores = [bm25_scores[i] for i in top_bm25_ids]

    bm25_scores_norm = normalize_scores(top_bm25_scores)
    # ==================================================
    # MERGE RESULTS
    # ==================================================

    merged = {}

    # Vector Results
    for idx, score in zip(faiss_ids[0], vector_scores):

        chunk = faiss_metadata[idx]

        merged[chunk["chunk_id"]] = {

            **chunk,

            "vector_score": float(score),

            "bm25_score": 0.0
        }

    # BM25 Results
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

    # ==================================================
    # FINAL HYBRID SCORE
    # ==================================================

    results = []

    query_lower = query.lower()

    for chunk in merged.values():

        chunk["hybrid_score"] = hybrid_score(

            chunk["vector_score"],

            chunk["bm25_score"],

            VECTOR_WEIGHT,

            BM25_WEIGHT
        )

        # ==================================================
        # DOCUMENT TYPE BOOSTING
        # ==================================================

        if chunk["doc_type"] == "tax":

            if any(word in query_lower for word in [
                "tax",
                "irs",
                "income",
                "deduction",
                "refund",
                "payroll"
            ]):

                chunk["hybrid_score"] += 0.20

        elif chunk["doc_type"] == "judgments":

            if any(word in query_lower for word in [
                "case",
                "judgment",
                "court",
                "decision",
                "versus",
                "v."
            ]):

                chunk["hybrid_score"] += 0.20

        elif chunk["doc_type"] == "acts":

            if any(word in query_lower for word in [
                "law",
                "act",
                "section",
                "statute",
                "constitution"
            ]):

                chunk["hybrid_score"] += 0.20

        elif chunk["doc_type"] == "pov":

            if any(word in query_lower for word in [
                "analysis",
                "overview",
                "summary",
                "explain"
            ]):

                chunk["hybrid_score"] += 0.10

        results.append(chunk)

    # ==================================================
    # REMOVE DUPLICATE CHUNKS
    # ==================================================

    results = remove_duplicates(results)

    # ==================================================
    # REMOVE LOW QUALITY CHUNKS
    # ==================================================

    results = [

        r for r in results

        if len(r["text"].split()) > 80
    ]

    # ==================================================
    # SORT
    # ==================================================

    results = sort_results(results)

    # ==================================================
    # KEEP BEST CHUNK PER DOCUMENT
    # ==================================================

    filtered = []

    seen_docs = set()

    for r in results:

        if r["filename"] not in seen_docs:

            filtered.append(r)

            seen_docs.add(r["filename"])

    results = filtered[:FINAL_RESULTS]

    # ==================================================
    # DISPLAY
    # ==================================================

    print("\n")
    print("=" * 90)
    print("HYBRID SEARCH RESULTS")
    print("=" * 90)

    for i, chunk in enumerate(results, start=1):

        print(f"\nResult #{i}")

        print("-" * 90)

        print(f"Hybrid Score : {chunk['hybrid_score']:.4f}")

        print(f"Vector Score : {chunk['vector_score']:.4f}")

        print(f"BM25 Score   : {chunk['bm25_score']:.4f}")

        print(f"Document     : {chunk['filename']}")

        print(f"Type         : {chunk['doc_type']}")

        print(f"Pages        : {chunk['page_start']} - {chunk['page_end']}")

        print("\nPreview:\n")

        print(chunk["text"][:600])

        print("\n" + "=" * 90)