# ⚖️ Legal RAG System (US Tax & Legal Research)

A Hybrid Retrieval-Augmented Generation (RAG) system for answering US tax and legal research questions from a collection of legal documents with document-level citations and page references.

---

# 📌 Project Overview

This project was developed as part of the Legal RAG assignment.

The system processes legal PDF documents, creates a hybrid retrieval pipeline using semantic search and keyword-based search, and generates grounded answers using a Large Language Model (LLM).

Supported document categories:

- Acts
- Court Judgments
- Point of View (POV)
- Tax Documents

The system provides:

- Accurate legal answers
- Source document references
- Page-level citations
- Supporting legal context

---

# 🚀 Features

- PDF Document Processing
- Text Extraction
- Document Metadata Extraction
- Intelligent Text Chunking
- Semantic Vector Search
- Keyword-Based Search
- Hybrid Retrieval Pipeline
- LLM-based Answer Generation
- Source Document Citations
- Page Number References
- Document Summarization
- FastAPI Backend
- Streamlit Interactive UI
- Golden Set Evaluation
- Retrieval Accuracy Measurement
- Faithfulness Evaluation

---

# 🏗️ Project Architecture

```
                 Legal PDF Documents
                         │
                         ▼
              PDF Parsing & Text Extraction
                         │
                         ▼
             Chunking + Metadata Extraction
        (Document Name, Page Number, Chunk ID)
                         │
                         ▼
              Embedding Generation
          (BAAI/bge-base-en-v1.5)
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        FAISS Index              BM25 Index
     (Semantic Search)       (Keyword Search)
              │                     │
              └──────────┬──────────┘
                         ▼
                Hybrid Retrieval
                         │
                         ▼
              Top Relevant Document Chunks
                         │
                         ▼
                Prompt Construction
                         │
                         ▼
              Groq Llama 3.1 8B Model
                         │
                         ▼
             Answer Generation + Citations
                         │
                         ▼
              FastAPI Backend + Streamlit UI
```

---

# 📂 Project Structure

```
legal-rag-system/

│
├── python/
│   ├── app.py
│   ├── streamlit_app.py
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
├── documents/
│
└── README.md
```

---

# ⚙️ Technologies Used

## Backend

- Python
- FastAPI
- Uvicorn

## Retrieval System

- FAISS
- BM25

## Embeddings

- Sentence Transformers
- BAAI/bge-base-en-v1.5

## Large Language Model

- Groq API
- Llama 3.1 8B Instant

## User Interface

- Streamlit

## Data Processing

- Pandas
- NumPy
- Pickle

---

# 📄 Data Processing Pipeline

## Step 1: PDF Processing

Legal PDF documents are loaded and processed.

The system extracts:

- Document text
- Document name
- Page number
- Document category


## Step 2: Text Chunking

Extracted text is divided into smaller chunks while maintaining metadata:

- Document name
- Page number
- Chunk ID


## Step 3: Embedding Generation

Text chunks are converted into embeddings using:

```
BAAI/bge-base-en-v1.5
```

Embeddings are stored in the FAISS vector index.


## Step 4: Index Creation

Two retrieval indexes are created:

### FAISS Index

Used for semantic similarity search.

### BM25 Index

Used for keyword-based retrieval.

---

# 🔍 Hybrid Retrieval Pipeline

For every user query:

1. Query embedding is generated.
2. FAISS performs semantic search.
3. BM25 performs keyword search.
4. Scores are normalized.
5. Both retrieval results are combined using weighted scoring.
6. Duplicate chunks are removed.
7. Highest-ranked chunks are selected.
8. Top relevant context is provided to the LLM.

---

# 🤖 LLM Answer Generation

Retrieved legal context is passed to Groq Llama 3.1.

The model is instructed to:

- Answer only from retrieved context.
- Avoid hallucinations.
- Provide document citations.
- Include page references.
- Mention supporting sources.

---

# 🌐 API Endpoints

## Health Check

```
GET /
```

Response:

```
Legal RAG API Running
```

---

## Question Answering

```
POST /ask
```

Example Request:

```json
{
  "question": "What does the Fair Labor Standards Act say about overtime pay?"
}
```

Returns:

- Generated answer
- Source documents
- Page references
- Supporting citations


---

## Document Summarization

```
POST /summarize
```

Example:

```json
{
    "question":"filename.pdf"
}
```

Returns:

- Document summary
- Source document reference

---

# 📊 Evaluation (Milestone 4)

Evaluation was performed using a Golden Set containing:

- 100 legal queries
- Ground truth answers
- Expected source documents


## Retrieval Accuracy

Checks whether retrieved documents match the expected source documents.

Result:

```
70% Retrieval Accuracy
```


## Faithfulness Evaluation

LLM-as-a-Judge evaluation was performed to measure answer grounding.

Result:

```
100% Partially Faithful
0% Unfaithful
```

---

# 📌 Example Response

```
Answer:

The Fair Labor Standards Act requires employers to pay eligible employees
overtime compensation at one and one-half times their regular rate for hours
worked beyond 40 hours in a workweek.


Primary Citation:

Document: CHRG-112hhrg67301.pdf
Pages: 47-47


Additional References:

USREPORTS-334-446.pdf
Pages: 41-42
```

---

# ▶️ Running the Project

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Start FastAPI Backend

```bash
cd python

uvicorn app:app --reload
```

---

## Start Streamlit Interface

Open another terminal:

```bash
cd python

streamlit run streamlit_app.py
```

---

## Run Evaluation

```bash
cd python/evaluation

python evaluate.py
```

---

# 📈 Final Deliverables

✅ Hybrid Legal RAG System

✅ PDF Processing Pipeline

✅ Semantic + Keyword Hybrid Retrieval

✅ FAISS Vector Search

✅ BM25 Keyword Search

✅ FastAPI Backend

✅ Streamlit Interactive Interface

✅ Question Answering System

✅ Document Summarization

✅ Source Citations

✅ Page-Level References

✅ Golden Set Evaluation

✅ Retrieval Accuracy Measurement

✅ Faithfulness Evaluation

✅ System Architecture Documentation