import joblib
from dotenv import load_dotenv
load_dotenv()

import os
from app.services.document_loader import load_document
from app.services.chunker import chunk_text
from app.services.embedding_service import EmbeddingService

DATA_DIR = "data"
EMBEDDING_DIR = "embeddings"

FILES = [
    "constitution.txt",
    "ipc.txt",
    "bns.txt"
]

def main():
    print("🔹 Loading documents...")
    all_chunks = []
    metadata = []

    for fname in FILES:
        path = os.path.join(DATA_DIR, fname)
        text = load_document(path)
        chunks = chunk_text(text)

        print(f"Loaded {fname}: {len(chunks)} chunks")

        all_chunks.extend(chunks)
        metadata.extend(chunks)


    print("🔹 Creating TF-IDF vectors...")
    embedder = EmbeddingService()
    vectors = embedder.fit_transform(all_chunks)

    os.makedirs(EMBEDDING_DIR, exist_ok=True)

    index_path = os.path.join(EMBEDDING_DIR, "index.faiss")
    meta_path = os.path.join(EMBEDDING_DIR, "metadata.txt")

    print("🔹 Saving vectorizer...")
    joblib.dump(embedder.vectorizer, "embeddings/vectorizer.pkl")

    print("🔹 Saving FAISS index...")
    embedder.save_faiss_index(vectors, metadata, index_path, meta_path)

    print("✅ DONE! TF-IDF FAISS index built successfully.")

if __name__ == "__main__":
    main()
