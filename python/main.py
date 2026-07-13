from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from .llm_answer import ask


app = FastAPI(
    title="Legal RAG API",
    description="US Tax & Legal Hybrid RAG System",
    version="1.0"
)

# Allow React frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later React URL se replace karenge
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "Legal RAG API Running 🚀"
    }


@app.post("/ask")
def ask_question(request: QueryRequest):

    result = ask(request.question)

    return result
    from .summarize import summarize_document

@app.post("/summarize")
def summarize_endpoint(request: QueryRequest):  # reuse same request model, "question" field me filename bhejo
    result = summarize_document(request.question)
    return result