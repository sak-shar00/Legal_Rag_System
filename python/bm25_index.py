import json
import pickle
from rank_bm25 import BM25Okapi
from preprocess import preprocess

print("Loading chunks...")

with open("../chunks.json", "r") as f:
    chunks = json.load(f)

corpus = []

for chunk in chunks:
    # Proper preprocessing
    tokens = preprocess(chunk["text"])
    corpus.append(tokens)

print("Building BM25...")

bm25 = BM25Okapi(corpus)

with open("bm25.pkl", "wb") as f:
    pickle.dump(bm25, f)

with open("bm25_metadata.pkl", "wb") as f:
    pickle.dump(chunks, f)

print("================================")
print("BM25 Index Created Successfully")
print("Total Documents :", len(chunks))
print("================================")