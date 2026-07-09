import pickle
import faiss

from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-base-en-v1.5"

print("Loading Model...")

model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS Index...")

index = faiss.read_index("faiss.index")

with open("metadata.pkl","rb") as f:
    metadata = pickle.load(f)

print("Ready!")

while True:

    query = input("\nAsk Question : ")

    if query.lower() == "exit":
        break

    query_vector = model.encode(
        [query],
        normalize_embeddings=True
    )

    scores, ids = index.search(query_vector, 10)

    print("\nTop Results\n")

    for score, idx in zip(scores[0], ids[0]):

        chunk = metadata[idx]

        print("=" * 80)

        print("Similarity :", score)

        print("Document :", chunk["filename"])

        print("Type :", chunk["doc_type"])

        print("Pages :", chunk["page_start"], "-", chunk["page_end"])

        print()

        print(chunk["text"][:700])

        print("\n")