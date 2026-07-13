"""
summarize.py
Legal RAG - Milestone 3 (Summarization Feature)

Generates a concise summary of an ENTIRE document (not just a Q&A answer).
Works for all 4 doc types: Acts, Judgments, POV, Tax.

APPROACH: Map-Reduce summarization
  1. Gather ALL chunks belonging to the requested document
  2. If the document is short enough, summarize it in one LLM call
  3. If it's long (most legal PDFs are), summarize it in groups first
     ("map"), then summarize those summaries into one final summary
     ("reduce") - this avoids exceeding the LLM's context window
"""

import os
import pickle

from dotenv import load_dotenv
from groq import Groq

# ============================================================
# LOAD ENV
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

client = Groq(api_key=API_KEY)
GROQ_MODEL = "llama-3.3-70b-versatile"

# How many chunks to combine per "map" call before reducing.
# Lower this if you hit context-length errors on very long documents.
CHUNKS_PER_GROUP = 6

# ============================================================
# LOAD ALL CHUNKS (reuse the same metadata your search already uses)
# ============================================================

bm25_metadata_path = os.path.join(BASE_DIR, "bm25_metadata.pkl")
with open(bm25_metadata_path, "rb") as f:
    all_chunks = pickle.load(f)


# ============================================================
# DOC-TYPE-SPECIFIC SUMMARY TEMPLATES
# ============================================================
# Different document types need different summary structures.
# A court judgment summary looks very different from a tax
# publication summary.

SUMMARY_TEMPLATES = {
    "judgments": """Summarize this court judgment/case excerpt. Structure your summary with:
- Facts: brief background of the dispute
- Issue: the legal question being decided
- Holding: what the court decided
- Reasoning: key reasoning behind the decision (if present in this excerpt)""",

    "acts": """Summarize this statute/act excerpt. Structure your summary with:
- Purpose: what this provision is meant to achieve
- Key Provisions: the main rules or requirements it establishes
- Who It Applies To: which parties/situations are covered""",

    "pov": """Summarize this legal commentary/analysis excerpt. Structure your summary with:
- Topic: what issue is being discussed
- Key Arguments: the main points made by the author
- Conclusion/Recommendation: what the author ultimately argues or recommends""",

    "tax": """Summarize this tax document/IRS publication excerpt. Structure your summary with:
- Subject: what tax topic this covers
- Key Rules: the main requirements, rates, or procedures described
- Practical Implications: what this means for a taxpayer or business""",
}

DEFAULT_TEMPLATE = """Summarize this legal document excerpt concisely, covering the main
points, any rules or decisions described, and why it matters."""


def get_document_chunks(filename):
    """Get all chunks for a given filename, sorted by page number."""
    matches = [c for c in all_chunks if c["filename"].lower() == filename.lower()]
    matches.sort(key=lambda c: c.get("page_start", 0))
    return matches


def generate(prompt):
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert Legal Research Assistant specializing in concise, accurate summaries."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def summarize_group(chunks, doc_type, filename):
    """'Map' step: summarize one group of chunks."""
    template = SUMMARY_TEMPLATES.get(doc_type, DEFAULT_TEMPLATE)

    combined_text = "\n\n".join(
        f"[Pages {c['page_start']}-{c['page_end']}]\n{c['text']}" for c in chunks
    )

    prompt = f"""{template}

Document: {filename}

Content:
{combined_text}

Summary:"""
    return generate(prompt)


def combine_summaries(partial_summaries, doc_type, filename):
    """'Reduce' step: combine multiple partial summaries into one final summary."""
    template = SUMMARY_TEMPLATES.get(doc_type, DEFAULT_TEMPLATE)

    combined = "\n\n---\n\n".join(
        f"[Section {i+1} Summary]\n{s}" for i, s in enumerate(partial_summaries)
    )

    prompt = f"""You are combining multiple section summaries of the same document into
ONE final, coherent, non-repetitive summary.

{template}

Document: {filename}

Section summaries to combine:
{combined}

Final combined summary:"""
    return generate(prompt)


def summarize_document(filename):
    """
    Main entry point. Returns a dict with the summary and metadata.
    """
    chunks = get_document_chunks(filename)

    if not chunks:
        return {
            "success": False,
            "answer": f"No document found with filename '{filename}' in the database.",
            "filename": filename,
        }

    doc_type = chunks[0].get("doc_type", "unknown")
    total_pages = max(c.get("page_end", 0) for c in chunks)

    try:
        if len(chunks) <= CHUNKS_PER_GROUP:
            # Short enough to summarize in one go
            final_summary = summarize_group(chunks, doc_type, filename)
        else:
            # MAP step: summarize in groups
            groups = [
                chunks[i:i + CHUNKS_PER_GROUP]
                for i in range(0, len(chunks), CHUNKS_PER_GROUP)
            ]
            partial_summaries = [
                summarize_group(group, doc_type, filename) for group in groups
            ]
            # REDUCE step: combine into one final summary
            final_summary = combine_summaries(partial_summaries, doc_type, filename)

        return {
            "success": True,
            "filename": filename,
            "doc_type": doc_type,
            "total_pages": total_pages,
            "chunks_used": len(chunks),
            "summary": final_summary,
        }

    except Exception as e:
        return {
            "success": False,
            "answer": str(e),
            "filename": filename,
        }


# ============================================================
# MAIN (CLI testing)
# ============================================================

if __name__ == "__main__":
    while True:
        filename = input("\nEnter document filename to summarize (or 'exit'): ").strip()
        if filename.lower() == "exit":
            break

        result = summarize_document(filename)

        print("\n" + "=" * 90)
        if result["success"]:
            print(f"SUMMARY: {result['filename']} ({result['doc_type']}, {result['total_pages']} pages, {result['chunks_used']} chunks used)")
            print("=" * 90)
            print(result["summary"])
        else:
            print("FAILED")
            print("=" * 90)
            print(result["answer"])
        print()