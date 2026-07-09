import json
import os
import pickle

import faiss
import numpy as np

from tqdm import tqdm
from sentence_transformers import SentenceTransformer


# -----------------------------
# CONFIG
# -----------------------------

CHUNKS_FILE = "../chunks.json"

INDEX_FILE = "faiss.index"

METADATA_FILE = "metadata.pkl"

MODEL_NAME = "BAAI/bge-base-en-v1.5"

BATCH_SIZE = 64

# -----------------------------
# LOAD MODEL
# -----------------------------

print("Loading Embedding Model...")

model = SentenceTransformer(MODEL_NAME)

print("Model Loaded Successfully.")

# -----------------------------
# LOAD CHUNKS
# -----------------------------

print("Loading Chunks...")

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Total Chunks : {len(chunks)}")

# -----------------------------
# EMBEDDINGS
# -----------------------------

embeddings = []

metadata = []

for i in tqdm(range(0, len(chunks), BATCH_SIZE)):

    batch = chunks[i:i+BATCH_SIZE]

    texts = [
        c["text"] for c in batch
    ]

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    embeddings.append(vectors)

    metadata.extend(batch)

embeddings = np.vstack(embeddings)

print("Embedding Shape :", embeddings.shape)

# -----------------------------
# BUILD FAISS
# -----------------------------

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print("FAISS Index Created")

# -----------------------------
# SAVE
# -----------------------------

faiss.write_index(index, INDEX_FILE)

with open(METADATA_FILE, "wb") as f:

    pickle.dump(metadata, f)

print("--------------------------------")

print("Saved Files")

print(INDEX_FILE)

print(METADATA_FILE)

print("--------------------------------")