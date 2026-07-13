# ⚖️ Legal RAG System (US Tax & Legal Research)

A Hybrid Retrieval-Augmented Generation (RAG) system for answering legal and tax-related questions from a collection of legal documents with document-level citations and page references.

---

# 📌 Project Overview

This project was developed as part of the Legal RAG assignment.

The system processes legal PDFs, builds a hybrid retrieval pipeline using semantic search and keyword search, and generates grounded answers using a Large Language Model (LLM).

Supported document categories:

- Acts
- Court Judgments
- Point of View (POV)
- Tax Documents

The system returns:

- Accurate legal answers
- Source document name
- Page references
- Supporting citations

---

# 🚀 Features

- PDF Parsing
- Text Chunking
- Metadata Extraction
- FAISS Vector Search
- BM25 Keyword Search
- Hybrid Retrieval
- LLM Answer Generation
- Source Citations
- Page References
- Document Summarization
- FastAPI Backend
- React Frontend
- Golden Set Evaluation
- Retrieval Accuracy Measurement
- Faithfulness Evaluation

---

# 🏗️ Project Architecture

```
100 Legal PDFs
        │
        ▼
PDF Parsing & Text Extraction
        │
        ▼
Chunking + Metadata
(Document, Page, Chunk ID)
        │
        ▼
Embedding Generation
(Sentence Transformer)
        │
        ├──────────────┐
        ▼              ▼
 FAISS Index      BM25 Index
(Vector Search) (Keyword Search)
        │              │
        └──────┬───────┘
               ▼
        Hybrid Retrieval
               ▼
      Top Relevant Chunks
               ▼
        Prompt Construction
               ▼
      Groq Llama 3.1 8B
               ▼
      Answer + Citations
               ▼
      FastAPI Response
```

---

# 📂 Project Structure

```
legal-rag-system/

│
├── python/
│   ├── app.py
│   ├── llm_answer.py
│   ├── preprocess.py
│   ├── build_index.py
│   ├── hybrid_search.py
│   ├── summarize.py
│   ├── utils.py
│   ├── config.py
│   │
│   ├── faiss.index
│   ├── metadata.pkl
│   ├── bm25.pkl
│   ├── bm25_metadata.pkl
│   │
│   └── evaluation/
│        ├── evaluate.py
│        ├── golden_set_FINAL_CLEAN.xlsx
│        └── evaluation_results_full.xlsx
│
├── frontend/
│
├── documents/
│
└── README.md
```

---

# ⚙️ Technologies Used

## Backend

- Python
- FastAPI

## Retrieval

- FAISS
- BM25

## Embeddings

- Sentence Transformers
- BAAI/bge-base-en-v1.5

## LLM

- Groq API
- Llama 3.1 8B Instant

## Frontend

- React

## Other

- Pandas
- NumPy
- Pickle
- Uvicorn

---

# 📄 Data Processing Pipeline

## Step 1

Load legal PDF documents.

## Step 2

Extract text while preserving:

- Document name
- Page number
- Document type

## Step 3

Split documents into chunks.

## Step 4

Generate embeddings using Sentence Transformers.

## Step 5

Create:

- FAISS Vector Index
- BM25 Keyword Index

---

# 🔍 Hybrid Retrieval

For every user query:

1. Generate query embedding.
2. Search FAISS.
3. Search BM25.
4. Normalize scores.
5. Combine using weighted hybrid score.
6. Remove duplicate chunks.
7. Keep highest scoring chunk per document.
8. Send Top-5 chunks to the LLM.

---

# 🤖 LLM Answer Generation

The retrieved chunks are passed to Groq Llama 3.1.

The model is instructed to:

- Answer only from retrieved context.
- Never hallucinate.
- Always provide citations.
- Include document names.
- Include page references.

---

# 🌐 API Endpoints

## Health Check

```
GET /
```

Returns:

```
Legal RAG API Running
```

---

## Question Answering

```
POST /ask
```

Example

```json
{
  "question": "What does the Fair Labor Standards Act say about overtime pay?"
}
```

Returns

- Answer
- Source documents
- Page references

---

## Document Summarization

```
POST /summarize
```

Example

```json
{
    "question":"filename.pdf"
}
```

Returns

- Summary
- Source document

---

# 📊 Evaluation (Milestone 4)

Evaluation was performed using a Golden Set containing:

- 100 Queries
- Ground Truth Answers
- Expected Source Documents

The evaluation measured:

## Retrieval Accuracy

Checks whether the retrieved document matches the expected source.

**Result**

**70% Retrieval Accuracy**

---

## Faithfulness

LLM-as-a-Judge compares generated answers with the Golden Set.

Result:

- 100% Partially Faithful
- 0% Unfaithful

---

# 📌 Example Response

```
Answer

The Fair Labor Standards Act requires employers to pay overtime at one and one-half times the regular rate for hours worked beyond 40 hours in a workweek.

Primary Citation

(Document: CHRG-112hhrg67301.pdf, Pages: 47-47)

Additional References

USREPORTS-334-446.pdf
Pages 41-42
```

---

# ▶️ Running the Project

## Backend

```bash
cd python

uvicorn app:app --reload
```

---

## Frontend

```bash
npm install

npm run dev
```

---

## Evaluation

```bash
cd python/evaluation

python evaluate.py
```

---

# 📈 Final Deliverables

✅ Hybrid Legal RAG System

✅ FastAPI Backend

✅ React Frontend

✅ Question Answering

✅ Document Summarization

✅ Source Citations

✅ Page References

✅ Golden Set Evaluation

✅ Architecture Diagram



