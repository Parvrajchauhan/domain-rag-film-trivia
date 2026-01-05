import numpy as np
from typing import List, Dict

from src.embedding.embedding_model import load_embedding_model


SECTION_WEIGHTS = {
    "plot_ending": 1.2,
    "summaries": 1.15,
    "lead_section": 1.1,
    "plot_build_up": 1.05,
    "plot_setup": 1.0,
    "synopsis": 1.0,
    "production": 0.9,
    "trivia": 0.85,
    "goofs_continuity": 0.7,
    "goofs_factual": 0.7,
    "reception": 0.6,
    "awards_finance": 0.6,
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
    top_k: int = 5,
) -> List[Dict]:
    
    if not retrieved_chunks:
        return []

    model = _get_embedding_model()

    query_emb = model.encode(
        query,
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

    reranked = []

    for chunk, emb in zip(retrieved_chunks, chunk_embs):
        sim = cosine_similarity(query_emb, emb)

        section = chunk.get("section", None)
        importance = SECTION_WEIGHTS.get(section, 1.0)

        final_score = sim * importance

        reranked.append({
            **chunk,
            "rerank_score": float(final_score),
            "base_similarity": float(sim),
            "importance": float(importance),
        })

    reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_k]
