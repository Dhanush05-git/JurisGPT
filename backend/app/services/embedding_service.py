# backend/app/services/embedding_service.py
import os
from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# FAISS import optional
try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    _FAISS_AVAILABLE = False

class EmbeddingService:
    """
    Simple TF-IDF -> FAISS embedding service.
    - fit_transform(texts): fits TF-IDF and returns numpy array (float32)
    - transform(texts): transforms with already-fitted vectorizer
    - save_faiss_index(vectors, texts, index_path, meta_path): saves index & metadata
    """

    def __init__(self):
        self.vectorizer: TfidfVectorizer | None = None

    def fit_transform(self, texts: List[str]) -> np.ndarray:
        self.vectorizer = TfidfVectorizer(max_features=32768, ngram_range=(1,2))
        X = self.vectorizer.fit_transform(texts)
        arr = X.astype("float32").toarray()
        return arr

    def transform(self, texts: List[str]) -> np.ndarray:
        if self.vectorizer is None:
            raise RuntimeError("Vectorizer not fitted")
        X = self.vectorizer.transform(texts)
        return X.astype("float32").toarray()

    def save_vectorizer(self, path: str):
        if self.vectorizer is None:
            raise RuntimeError("No vectorizer to save")
        dirn = os.path.dirname(path)
        if dirn:
            os.makedirs(dirn, exist_ok=True)
        joblib.dump(self.vectorizer, path)


    def load_vectorizer(self, path: str):
        self.vectorizer = joblib.load(path)

    def save_faiss_index(self, vectors: np.ndarray, texts: List[str], index_path: str, meta_path: str):
        """
        Save FAISS index and metadata. If FAISS not available, save vectors as numpy and metadata as text.
        """
        os.makedirs(os.path.dirname(index_path), exist_ok=True)

        if _FAISS_AVAILABLE:
            d = vectors.shape[1]
            index = faiss.IndexFlatL2(d)
            index.add(vectors)
            faiss.write_index(index, index_path)
        else:
            # fallback: save numpy vectors
            np.save(index_path + ".npy", vectors)

        # save metadata (one chunk per line)
        with open(meta_path, "w", encoding="utf-8") as f:
            for t in texts:
                # replace newlines to keep single-line metadata
                f.write(t.replace("\n", " ") + "\n")
