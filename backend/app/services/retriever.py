import os
from rank_bm25 import BM25Okapi
import numpy as np
import faiss
import joblib
import re

class Retriever:
    def __init__(self, index_path="embeddings/index.faiss", meta_path="embeddings/metadata.txt"):
        
        # Load text chunks
        with open(meta_path, "r", encoding="utf-8") as f:
            self.chunks = f.read().splitlines()

        # Preprocess for BM25
        tokenized_corpus = [chunk.lower().split() for chunk in self.chunks]

        # Initialize BM25
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, k: int = 3):
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

    

        # Extract number (21)
        match = re.search(r'\b(\d+)\b', query)
        number_match = match.group(1) if match else None

        query_lower = query.lower()

        for i, chunk in enumerate(self.chunks):
            chunk_lower = chunk.lower()

            # ⭐ EXACT number match boost (same as before)
            if number_match:
                if f"article {number_match}" in chunk_lower or f"section {number_match}" in chunk_lower:
                    scores[i] += 100
            print(">>> Using UPDATED RETRIEVER LOGIC")

            # ⭐ CATEGORY penalty logic
            if "article" in query_lower:
                # If it's asking for an Article, penalize IPC/BNS
                if "section" in chunk_lower:
                    scores[i] -= 50
            print(">>> Using UPDATED RETRIEVER LOGIC")

            if "section" in query_lower:
                # If asking for a Section, penalize Articles
                if "article" in chunk_lower:
                    scores[i] -= 50
            print(">>> Using UPDATED RETRIEVER LOGIC")

        top_k_indices = np.argsort(scores)[::-1][:k]
        return [self.chunks[i] for i in top_k_indices]

