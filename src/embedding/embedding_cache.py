import hashlib
import os
import pickle
from typing import Optional

class EmbeddingCache:

    def __init__(self, cache_dir: str = "data/embeddings/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _key(self, text: str) -> str:
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> Optional[list]:
        path = os.path.join(self.cache_dir, self._key(text))
        if os.path.exists(path):
            with open(path, "rb") as f:
                return pickle.load(f)
        return None

    def set(self, text: str, embedding):
        path = os.path.join(self.cache_dir, self._key(text))
        with open(path, "wb") as f:
            pickle.dump(embedding, f)
