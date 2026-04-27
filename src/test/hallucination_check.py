from __future__ import annotations

_ABSTAIN_PHRASES = {
    "i don't know based on the given context.",
    "i could not find the answer in the provided context.",
    "i don't know.",
}

# Per-query-type multipliers applied to the base threshold.
# Lower multiplier → easier to pass → harder to flag as hallucination.
_THRESHOLD_MULTIPLIERS: dict[str, float] = {
    "ending":      0.60,
    "explanation": 0.60,
    "general":     0.90,
    "plot":        0.80,
    "character":   0.80,
    "summary":     0.85,
    "fact":        1.00,
    "director":    1.00,
}


def hallucination_score(
    answer: str,
    context_chunks: list[dict],
    model,
    label: str,
    threshold: float = 0.55,
) -> dict:
    """
    Returns:
        score           float — cross-encoder score normalised by answer length
        is_hallucinated bool
    """
    # Empty answer → treat as hallucination
    if not answer or not answer.strip():
        return {"score": 0.0, "is_hallucinated": True}

    answer_norm = answer.strip().lower()

    # Abstention is a valid grounded response (model correctly said IDK)
    if answer_norm in _ABSTAIN_PHRASES:
        return {"score": 1.0, "is_hallucinated": False}

    # Labels that already confirm grounding — skip expensive model call
    grounded_labels = {"grounded_correct", "leaked_correct", "retrieved_but_wrong"}
    if label in grounded_labels:
        return {"score": 1.0, "is_hallucinated": False}

    # No context at all → cannot be grounded
    if not context_chunks:
        return {"score": 0.0, "is_hallucinated": True}

    query_type = context_chunks[0].get("query_type", "general")

    context_text = " ".join(
        c["text"] for c in context_chunks if isinstance(c, dict) and "text" in c
    )[:4000]

    raw_score = float(model.predict([(answer, context_text)])[0])
    # Normalise by answer word count to penalise long, unsupported answers
    word_count = max(len(answer.split()), 1)
    normalised = raw_score / word_count

    multiplier = _THRESHOLD_MULTIPLIERS.get(query_type, 1.0)
    effective_threshold = threshold * multiplier

    return {
        "score": round(normalised, 4),
        "is_hallucinated": normalised < effective_threshold,
    }