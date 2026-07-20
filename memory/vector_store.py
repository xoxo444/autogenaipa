import os
import json
import uuid
import numpy as np
import faiss

from memory.embedding_service import EmbeddingService


class VectorStore:
    def __init__(self, path="memory/faiss_store"):
        self.embedding = EmbeddingService()

        os.makedirs(path, exist_ok=True)

        self.index_path = os.path.join(path, "memory.index")
        self.meta_path = os.path.join(path, "memory.json")

        self.dimension = 384

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatIP(self.dimension)

        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = []

    def save(self):
        faiss.write_index(self.index, self.index_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

    def add(self, text, metadata=None):

        metadata = metadata or {}

        vector = np.array(
            [self.embedding.embed(text)],
            dtype=np.float32
        )

        faiss.normalize_L2(vector)

        memory = {
            "id": str(uuid.uuid4()),
            "text": text,
            "metadata": metadata,
        }

        self.index.add(vector)
        self.metadata.append(memory)

        self.save()

    def search(self, query, k=5):

        if len(self.metadata) == 0:
            return []

        vector = np.array(
            [self.embedding.embed(query)],
            dtype=np.float32
        )

        faiss.normalize_L2(vector)

        scores, indices = self.index.search(
            vector,
            min(k, len(self.metadata))
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            memory = self.metadata[idx].copy()
            memory["score"] = float(score)

            results.append(memory)

        return results