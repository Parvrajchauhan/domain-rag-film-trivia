import numpy as np
from typing import List, Dict
from src.embeddings.embedder import embed_text


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def rerank(
    query: str,
    retrieved_chunks: List[Dict],
    top_k: int = 5
) -> List[Dict]:
    """
    Step 2: Semantic reranking
    """
    query_emb = embed_text(query)
    query_emb = np.array(query_emb)

    reranked = []

    for chunk in retrieved_chunks:
        chunk_emb = embed_text(chunk["text"])
        chunk_emb = np.array(chunk_emb)

        sim = cosine_similarity(query_emb, chunk_emb)

        chunk["rerank_score"] = sim
        reranked.append(chunk)

    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_k]
