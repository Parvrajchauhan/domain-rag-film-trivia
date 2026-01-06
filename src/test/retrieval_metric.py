from typing import List, Set


def _match(text: str, relevant_set: Set[str]) -> bool:
    """
    Checks whether any relevant fact string appears in the text.
    Used for Recall@K (fact coverage).
    """
    text = text.lower()
    return any(rel.lower() in text for rel in relevant_set)


def precision_at_k(
    query: str,
    retrieved_chunks: List[dict],
    model,
    k: int = 5,
    relevance_threshold: float = 0.6
) -> float:

    if not retrieved_chunks:
        return 0.0

    chunks = retrieved_chunks[:k]

    chunks = [c for c in chunks if isinstance(c, dict) and "text" in c]

    if not chunks:
        return 0.0

    pairs = [(query, c["text"]) for c in chunks]
    scores = model.predict(pairs)

    relevant = sum(score >= relevance_threshold for score in scores)

    return relevant / len(chunks)


def recall_at_k(
    retrieved_chunks: List[dict],
    relevant_set: Set[str],
    k: int = 5
) -> float:
    """
    Recall@K:
    Returns 1.0 if ANY of the top-k chunks contains
    a relevant fact, else 0.0.
    """

    if not retrieved_chunks or not relevant_set:
        return 0.0

    chunks = retrieved_chunks[:k]

    for c in chunks:
        if not isinstance(c, dict) or "text" not in c:
            continue

        if _match(c["text"], relevant_set):
            return 1.0

    return 0.0
