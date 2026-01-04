import faiss
import numpy as np
from typing import List, Dict
from src.embeddings.embedder import embed_text
from src.db.metadata import fetch_metadata_by_ids


def retrieve(
    query: str,
    index: faiss.Index,
    k: int = 10
) -> List[Dict]:
    """
    Step 1: Vector retrieval
    """
    query_embedding = embed_text(query)
    query_embedding = np.array([query_embedding]).astype("float32")

    scores, ids = index.search(query_embedding, k)

    chunks = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:
            continue

        metadata = fetch_metadata_by_ids(idx)

        chunks.append({
            "chunk_id": idx,
            "score": float(score),
            "text": metadata["text"],
            "title": metadata.get("title"),
            "source": metadata.get("source")
        })

    return chunks
