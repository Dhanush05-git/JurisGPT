import os
import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class EmbeddingService:
    def __init__(self):
        # Use a simple TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000
        )

    def fit_transform(self, texts):
        vectors = self.vectorizer.fit_transform(texts).toarray()
        return vectors

    def save_faiss_index(self, vectors, metadata, index_path, meta_path):
        vectors = np.array(vectors).astype("float32")
        dim = vectors.shape[1]

        index = faiss.IndexFlatL2(dim)
        index.add(vectors)

        faiss.write_index(index, index_path)

        with open(meta_path, "w", encoding="utf-8") as f:
            for m in metadata:
                f.write(m + "\n")
