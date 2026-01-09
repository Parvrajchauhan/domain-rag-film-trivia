def hallucination_score(
    answer: str,
    context_chunks: list[dict],
    model,
    threshold: float = 0.55
) -> dict:
    """
    Returns:
      score: float in [0, 1] (higher = more grounded)
      is_hallucinated: bool
    """

    # 1️⃣ Empty answer
    if not answer or not answer.strip():
        return {"score": 0.0, "is_hallucinated": True}

    # 2️⃣ Explicit abstention
    if answer.strip().lower() in {
        "i don't know.",
        "i don't know based on the given context.",
        "not enough information in the context."
    }:
        return {"score": 1.0, "is_hallucinated": False}

    # 3️⃣ No context
    if not context_chunks:
        return {"score": 0.0, "is_hallucinated": True}

    # 4️⃣ Query type
    query_type = context_chunks[0].get("query_type", "general")

    # 5️⃣ Context text
    context_text = " ".join(c.get("text", "") for c in context_chunks)[:4000]

    # 6️⃣ Entailment score (model assumed to output similarity-like score)
    raw_score = float(model.predict([(answer, context_text)])[0])

    # ✅ Proper normalization (sigmoid-style clamp)
    normalized_score = max(0.0, min(raw_score, 1.0))

    # 7️⃣ Adaptive threshold
    effective_threshold = threshold
    if query_type in {"ending", "explanation"}:
        effective_threshold *= 0.6
    elif query_type == "general":
        effective_threshold *= 0.9

    is_hallucinated = normalized_score < effective_threshold

    return {
        "score": round(normalized_score, 4),
        "is_hallucinated": is_hallucinated
    }

def compute_confidence(
    chunks: list[dict],
    hallucination_score: float
) -> float:
    """
    hallucination_score: float in [0,1] (higher = more grounded)
    """

    if not chunks:
        return 0.0

    # 1️⃣ Prefer reranker
    def get_score(c):
        if "rerank_score" in c:
            return float(c["rerank_score"])
        return float(c.get("base_similarity", 0.0))

    # 2️⃣ Sort by evidence strength
    chunks = sorted(chunks, key=get_score, reverse=True)

    # 3️⃣ Top-K weighted evidence
    weights = [0.5, 0.3, 0.2]
    evidence_score = 0.0

    for i, w in enumerate(weights):
        if i < len(chunks):
            evidence_score += get_score(chunks[i]) * w

    # 4️⃣ Combine grounding + evidence
    confidence = evidence_score * hallucination_score

    return round(max(0.0, min(confidence, 1.0)), 3)
