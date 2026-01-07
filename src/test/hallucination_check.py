def hallucination_score(
    answer: str,
    context_chunks: list[dict],
    model,
    threshold: float = 0.55
) -> dict:
  
    if not answer:
        return {
            "score": 0.0,
            "is_hallucinated": True
        }

    if answer.strip() == "I don't know based on the given context.":
        return {
            "score": 1.0,
            "is_hallucinated": False
        }

    if not context_chunks:
        return {
            "score": 0.0,
            "is_hallucinated": True
        }

    query_type = context_chunks[0].get("query_type", "general")

    if query_type in {"fact", "director"}:
        return {
            "score": 1.0,
            "is_hallucinated": False
        }

    context_text = " ".join(c["text"] for c in context_chunks)
    context_text = context_text[:4000]

    raw_score = float(
        model.predict([(answer, context_text)])[0]
    )

    normalized_score = raw_score / max(len(answer.split()), 1)

    effective_threshold = threshold

    if query_type in {"ending", "explanation"}:
        effective_threshold *= 0.6 

    if query_type == "general":
        effective_threshold *= 0.9

    is_hallucinated = normalized_score < effective_threshold

    return {
        "score": round(normalized_score, 4),
        "is_hallucinated": is_hallucinated
    }
