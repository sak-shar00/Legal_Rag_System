# Dockerfile for Hugging Face Spaces deployment
# HF Spaces free tier gives 16GB RAM - enough for sentence-transformers + FAISS

FROM python:3.10-slim

WORKDIR /app

# System dependencies needed by some packages (faiss, numpy build chain)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better Docker layer caching - rebuilds are faster)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code
# IMPORTANT: this copies everything in your project folder into /app,
# including faiss.index, bm25.pkl, metadata.pkl, chunks.json etc.
COPY . .

# Hugging Face Spaces expects the app to listen on port 7860
ENV PORT=7860
EXPOSE 7860

# IMPORTANT: your main.py is at python/main.py, and llm_answer.py uses
# relative imports (from .config import ...), which means "python" must
# be a proper Python package - it needs an __init__.py file inside it.
# If that file doesn't exist yet, create an empty one:
#   touch python/__init__.py
CMD ["uvicorn", "python.main:app", "--host", "0.0.0.0", "--port", "7860"]