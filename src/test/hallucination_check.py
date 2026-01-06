def hallucination_score(
    answer: str,
    context_chunks: list[dict],
    model,
    threshold: float = 0.55
) -> dict:
    

    if not answer or not context_chunks:
        return {
            "score": 0.0,
            "is_hallucinated": True
        }

    context_text = " ".join(c["text"] for c in context_chunks)
    context_text = context_text[:4000]  # safety cap

    score = float(
        model.predict([(answer, context_text)])[0]
    )

    return {
        "score": score,
        "is_hallucinated": score < threshold
    }
