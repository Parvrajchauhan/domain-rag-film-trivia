import numpy as np
from typing import List, Dict
from src.embedding.embedding_model import load_embedding_model

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = load_embedding_model()
    return _model


def _tokenize_answer(answer: str) -> List[str]:
    return [t.lower() for t in answer.split() if t.isalpha()]


def _hard_filter(answer: str, chunk_text: str) -> bool:
    tokens = _tokenize_answer(answer)
    text = chunk_text.lower()
    return any(tok in text for tok in tokens)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


def filter_supported_chunks(
    answer: str,
    chunks: List[Dict],
    sim_threshold: float = 0.55
) -> List[Dict]:

    if not answer or not chunks:
        return []

    model = _get_model()

    answer_emb = model.encode(
        answer,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    answer_emb = np.asarray(answer_emb, dtype="float32")

    texts = [c["text"] for c in chunks]
    chunk_embs = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    chunk_embs = np.asarray(chunk_embs, dtype="float32")

    supported = []

    for chunk, emb in zip(chunks, chunk_embs):

        # Stage 1 — hard filter
        if not _hard_filter(answer, chunk["text"]):
            continue

        # Stage 2 — semantic filter
        sim = _cosine(answer_emb, emb)
        if sim < sim_threshold:
            continue

        supported.append({
            **chunk,
            "support_score": float(sim)
        })

    return supported
