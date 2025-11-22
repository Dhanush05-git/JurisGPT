# backend/app/services/retriever.py
import os
import json
import joblib
import numpy as np
import re
from typing import List, Optional

from rank_bm25 import BM25Okapi

# Try FAISS optional import
try:
    import faiss
    _FAISS_AVAILABLE = True
except Exception:
    faiss = None
    _FAISS_AVAILABLE = False

ACTIVE_FILE = "backend/data/active_version.json"
EMBED_ROOT = "backend/embeddings/versions"

class Retriever:
    """
    Retriever that:
    - Reads active version from backend/data/active_version.json
    - Loads metadata (chunks) and builds BM25
    - Loads FAISS index OR numpy vectors fallback
    - Loads saved vectorizer (joblib) to convert query -> vector if available
    - Performs hybrid search (bm25 + faiss similarity)
    """

    def __init__(self, bm25_weight: float = 0.4, faiss_weight: float = 0.6):
        self.bm25_weight = bm25_weight
        self.faiss_weight = faiss_weight

        self.active_version: Optional[str] = None
        self.chunks: List[str] = []
        self.bm25: Optional[BM25Okapi] = None
        self.vectorizer = None
        self.faiss_index = None
        self.vectors_np = None  # fallback numpy vectors
        # initialize from active file
        self._load_active_version_assets()

    def _read_active_version(self) -> Optional[str]:
        if not os.path.exists(ACTIVE_FILE):
            return None
        try:
            with open(ACTIVE_FILE, "r", encoding="utf-8") as f:
                js = json.load(f)
                return js.get("active_version")
        except Exception:
            return None

    def _load_active_version_assets(self):
        version_id = self._read_active_version()
        if not version_id:
            # no active version set
            self.active_version = None
            self.chunks = []
            self.bm25 = None
            self.vectorizer = None
            self.faiss_index = None
            self.vectors_np = None
            return

        # if already loaded and same id, skip
        if version_id == self.active_version:
            return

        # load metadata/chunks
        meta_path = os.path.join(EMBED_ROOT, version_id, "metadata.txt")
        vec_path = os.path.join(EMBED_ROOT, version_id, "vectorizer.pkl")
        index_path = os.path.join(EMBED_ROOT, version_id, "index.faiss")
        index_npy_path = index_path + ".npy"  # fallback if saved as numpy

        if not os.path.exists(meta_path):
            # nothing to load
            self.active_version = None
            self.chunks = []
            self.bm25 = None
            self.vectorizer = None
            self.faiss_index = None
            self.vectors_np = None
            return

        with open(meta_path, "r", encoding="utf-8") as f:
            chunks = [line.rstrip() for line in f.read().splitlines() if line.strip()]

        # build BM25
        tokenized_corpus = [c.lower().split() for c in chunks]
        self.chunks = chunks
        self.bm25 = BM25Okapi(tokenized_corpus) if tokenized_corpus else None

        # load vectorizer if present
        try:
            if os.path.exists(vec_path):
                self.vectorizer = joblib.load(vec_path)
            else:
                self.vectorizer = None
        except Exception:
            self.vectorizer = None

        # load FAISS index or numpy vectors fallback
        self.faiss_index = None
        self.vectors_np = None
        if _FAISS_AVAILABLE and os.path.exists(index_path):
            try:
                self.faiss_index = faiss.read_index(index_path)
            except Exception:
                self.faiss_index = None

        if self.faiss_index is None and os.path.exists(index_npy_path):
            try:
                self.vectors_np = np.load(index_npy_path)
                # if faiss not available we will use numpy arrays directly for similarity
            except Exception:
                self.vectors_np = None

        self.active_version = version_id

    def _ensure_current(self):
        # If active version changed on disk, reload
        current_active = self._read_active_version()
        if current_active != self.active_version:
            self._load_active_version_assets()

    def _boost_and_penalty(self, query: str, scores: np.ndarray) -> np.ndarray:
        """
        Apply simple domain logic:
        - exact Article/Section number boost
        - penalize mismatched categories (Article vs Section) based on query
        """
        # Extract number if present
        match = re.search(r'\b(\d+)\b', query)
        number_match = match.group(1) if match else None
        q_lower = query.lower()

        for i, chunk in enumerate(self.chunks):
            chunk_lower = chunk.lower()
            if number_match:
                if f"article {number_match}" in chunk_lower or f"section {number_match}" in chunk_lower:
                    scores[i] += 100.0
            # category penalty
            if "article" in q_lower and "section" in chunk_lower and "article" not in chunk_lower:
                scores[i] -= 40.0
            if "section" in q_lower and "article" in chunk_lower and "section" not in chunk_lower:
                scores[i] -= 40.0

        return scores

    def _faiss_scores_for_query(self, query: str) -> Optional[np.ndarray]:
        """
        Returns similarity scores (higher is better) aligned to chunks indices.
        If neither FAISS nor numpy vectors exist or vectorizer missing, returns None.
        """
        if (self.faiss_index is None) and (self.vectors_np is None):
            return None
        if self.vectorizer is None:
            # cannot compute query vector without vectorizer
            return None

        q_vec = self.vectorizer.transform([query]).astype("float32").toarray()
        if self.faiss_index is not None:
            # faiss returns distances — convert to similarity by negating distances
            D, I = self.faiss_index.search(q_vec, k=len(self.chunks))
            # D shape (1, n) ; I shape (1, n)
            dists = D[0]
            # convert to similarity-like (smaller distance -> larger score)
            # we'll use negative distance
            sim_scores = -dists.astype(np.float32)
            # map indices from I[0]
            # create vector of zeros then fill positions
            scores = np.zeros(len(self.chunks), dtype=np.float32)
            for idx_pos, idx in enumerate(I[0]):
                if idx < len(scores):
                    scores[idx] = sim_scores[idx_pos]
            return scores
        else:
            # use numpy vectors: compute cos similarity
            # normalize vectors
            try:
                vecs = self.vectors_np.astype(np.float32)
                q = q_vec[0].astype(np.float32)
                # cosine similarity
                vecs_norm = vecs / (np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12)
                q_norm = q / (np.linalg.norm(q) + 1e-12)
                sims = vecs_norm.dot(q_norm)
                return sims.astype(np.float32)
            except Exception:
                return None

    def search(self, query: str, k: int = 3) -> List[str]:
        """
        Returns top-k chunks (strings) for the given query.
        Hybrid scoring: combined bm25 + faiss similarity when both available.
        """
        self._ensure_current()

        if not self.chunks:
            return []

        # BM25 scores
        bm25_scores = np.zeros(len(self.chunks), dtype=np.float32)
        if self.bm25 is not None:
            tokenized_query = query.lower().split()
            try:
                bm25_raw = self.bm25.get_scores(tokenized_query)
                bm25_scores = np.array(bm25_raw, dtype=np.float32)
            except Exception:
                bm25_scores = np.zeros(len(self.chunks), dtype=np.float32)

        # FAISS / vector scores
        faiss_scores = self._faiss_scores_for_query(query)

        # Combine
        if faiss_scores is not None:
            # normalize both arrays to 0-1
            def _norm(x):
                if np.all(np.isfinite(x)) and x.size and (x.max() - x.min()) > 1e-12:
                    x2 = (x - x.min()) / (x.max() - x.min())
                    return x2
                else:
                    return np.zeros_like(x)
            bm_n = _norm(bm25_scores)
            fa_n = _norm(faiss_scores)
            combined = bm_n * self.bm25_weight + fa_n * self.faiss_weight
        else:
            combined = bm25_scores  # only BM25 available

        # apply boosts/penalties domain-specific
        combined = self._boost_and_penalty(query, combined)

        top_k_indices = np.argsort(combined)[::-1][:k]
        return [self.chunks[i] for i in top_k_indices if i < len(self.chunks)]
