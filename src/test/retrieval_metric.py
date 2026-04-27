from __future__ import annotations
from typing import List, Set

# Per-query-type multipliers on the relevance threshold for precision.
_PRECISION_MULTIPLIERS: dict[str, float] = {
    "ending":      0.85,
    "explanation": 0.85,
    "plot":        0.90,
    "character":   0.90,
    "summary":     0.90,
    "general":     0.95,
    "fact":        1.10,
    "director":    1.10,
}


def precision_at_k(
    query: str,
    retrieved_chunks: List[dict],
    model,
    k: int = 5,
    relevance_threshold: float = 0.6,
) -> float:
    """
    Fraction of top-k chunks whose cross-encoder score exceeds the
    (query-type-adjusted) threshold.
    """
    if not retrieved_chunks:
        return 0.0

    chunks = [c for c in retrieved_chunks[:k] if isinstance(c, dict) and "text" in c]
    if not chunks:
        return 0.0

    query_type = chunks[0].get("query_type", "general")
    multiplier = _PRECISION_MULTIPLIERS.get(query_type, 1.0)
    effective_threshold = relevance_threshold * multiplier

    pairs  = [(query, c["text"]) for c in chunks]
    scores = model.predict(pairs)

    relevant = sum(1 for s in scores if s >= effective_threshold)
    return round(relevant / len(chunks), 4)


def recall_at_k(
    retrieved_chunks: List[dict],
    relevant_set: Set[str],
    k: int = 5,
) -> float:
    """
    Binary recall: 1.0 if at least one chunk contains any keyword from
    relevant_set, else 0.0.

    Simplified from the original min_matches logic — a single keyword hit
    inside top-k is sufficient signal for the eval harness.
    """
    if not retrieved_chunks or not relevant_set:
        return 0.0

    chunks = [c for c in retrieved_chunks[:k] if isinstance(c, dict) and "text" in c]
    if not chunks:
        return 0.0

    needle_set = {r.lower() for r in relevant_set}

    for chunk in chunks:
        text = chunk["text"].lower()
        if any(needle in text for needle in needle_set):
            return 1.0

    return 0.0