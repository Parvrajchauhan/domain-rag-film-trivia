import numpy as np
from typing import List, Dict
from collections import defaultdict

from src.embedding.embedding_model import load_embedding_model


QUERY_TYPE_WEIGHTS = {
    "fact": 1.3,
    "director": 1.35,
    "ending": 1.25,
    "plot": 1.2,
    "character": 1.2,
    "explanation": 1.15,
    "summary": 1.2,
    "general": 1.0,
}

SECTION_WEIGHTS = {
    "plot_setup": 1.3,
    "plot_build_up": 1.3,
    "plot_ending": 1.4,
    "imdb_synopsis": 1.2,
    "lead_section": 1.1,
    "imdb_metadata": 1.2,
    "production": 0.8,
    "reception": 0.7,
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

        section = (chunk.get("section") or "").lower()
        section_weight = SECTION_WEIGHTS.get(section, 1.0)

        final_score = sim * intent_weight * section_weight

        if final_score < min_score:
            continue

        reranked.append({
            **chunk,
            "rerank_score": float(final_score),
            "base_similarity": float(sim),
            "query_type": query_type,
        })

    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

    doc_counts = defaultdict(int)
    final_results = []

    for chunk in reranked:
        doc_id = chunk.get("doc_id")

        if doc_counts[doc_id] >= 2:
            continue

        final_results.append(chunk)
        doc_counts[doc_id] += 1

        if len(final_results) >= top_k:
            break

    return final_results