import re
from sentence_transformers import CrossEncoder


def load_judge_model() -> CrossEncoder:
    return CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
    device="cpu",
    local_files_only=False,
)


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def exact_match(
    generated_answer: str,
    ground_truth: str,
    model: CrossEncoder,
    threshold: float = 0.8,
) -> dict:
    """
    Returns:
        score        float  — semantic similarity in [0, 1]
        exact_match  bool   — True if answer matches ground truth
    """
    if not generated_answer or not ground_truth:
        return {"score": 0.0, "exact_match": False}

    # Fast string check first (avoids model call for obvious hits)
    gen_norm = _normalize(generated_answer)
    gt_norm  = _normalize(ground_truth)

    if gt_norm in gen_norm or gen_norm in gt_norm:
        return {"score": 1.0, "exact_match": True}

    # Abstention is never a match
    abstain_phrases = {
        "i don't know based on the given context.",
        "i could not find the answer in the provided context.",
        "i don't know.",
    }
    if gen_norm in abstain_phrases:
        return {"score": 0.0, "exact_match": False}

    semantic_score = float(model.predict([(generated_answer, ground_truth)])[0])
    # ms-marco scores are unbounded; clamp to [0, 1] for consistency
    semantic_score = max(0.0, min(1.0, semantic_score))

    return {
        "score": round(semantic_score, 4),
        "exact_match": semantic_score >= threshold,
    }