from typing import List, Set


def _match(text: str, relevant_set: Set[str]) -> bool:
    
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

    chunks = [
        c for c in retrieved_chunks[:k]
        if isinstance(c, dict) and "text" in c
    ]

    if not chunks:
        return 0.0

    query_type = chunks[0].get("query_type", "general")

    effective_threshold = relevance_threshold
    if query_type in {"ending", "explanation"}:
        effective_threshold *= 0.85
    elif query_type in {"fact", "director"}:
        effective_threshold *= 1.1

    pairs = [(query, c["text"]) for c in chunks]
    scores = model.predict(pairs)

    relevant = 0
    for score in scores:
        if score >= effective_threshold:
            relevant += 1

    return relevant / len(chunks)


def recall_at_k(
    retrieved_chunks: List[dict],
    relevant_set: Set[str],
    k: int = 5,
    min_matches: int = 1
) -> float:
   
    if not retrieved_chunks or not relevant_set:
        return 0.0

    chunks = [
        c for c in retrieved_chunks[:k]
        if isinstance(c, dict) and "text" in c
    ]

    if not chunks:
        return 0.0

    matches = 0
    for c in chunks:
        if _match(c["text"], relevant_set):
            matches += 1
            if matches >= min_matches:
                return 1.0

    return 0.0
