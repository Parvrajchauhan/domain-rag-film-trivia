import numpy as np
from typing import List, Dict

from src.embedding.embedding_model import load_embedding_model


QUERY_TYPE_WEIGHTS = {
    "fact": 1.25,
    "director": 1.25,
    "ending": 1.2,
    "plot": 1.15,
    "character": 1.15,
    "explanation": 1.1,
    "summary": 1.15,
    "general": 1.0,
}


_embedding_model = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = load_embedding_model()
    return _embedding_model


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


def rerank(
    query: str,
    retrieved_chunks: List[Dict],
    query_type: str,                    
    top_k: int = 5,
    min_score: float = 0.15,
) -> List[Dict]:

    if not retrieved_chunks:
        return []

    model = _get_embedding_model()

    rewritten_query = retrieved_chunks[0].get("rewritten_query", query)

    query_emb = model.encode(
        rewritten_query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    query_emb = np.asarray(query_emb, dtype="float32")

    texts = [c["text"] for c in retrieved_chunks]

    chunk_embs = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    chunk_embs = np.asarray(chunk_embs, dtype="float32")

    intent_weight = QUERY_TYPE_WEIGHTS.get(query_type, 1.0)

    reranked = []

    for chunk, emb in zip(retrieved_chunks, chunk_embs):
        sim = cosine_similarity(query_emb, emb)

        final_score = sim * intent_weight

        if final_score < min_score:
            continue

        reranked.append({
            **chunk,
            "rerank_score": float(final_score),
            "base_similarity": float(sim),
            "query_type": query_type,
            "importance": float(intent_weight),
        })

    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

    deduped = {}
    for chunk in reranked:
        doc_id = chunk.get("doc_id")
        if doc_id not in deduped:
            deduped[doc_id] = chunk

    return list(deduped.values())[:top_k]
