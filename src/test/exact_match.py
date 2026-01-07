from sentence_transformers import CrossEncoder
import re


def load_judge_model():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def _normalize(text: str) -> str:
   
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def exact_match(
    generated_answer: str,
    ground_truth: str,
    model: CrossEncoder,
    threshold: float = 0.8
) -> dict:

    if not generated_answer or not ground_truth:
        return {
            "score": 0.0,
            "exact_match": False
        }

    gen_norm = _normalize(generated_answer)
    gt_norm = _normalize(ground_truth)

    if gt_norm in gen_norm or gen_norm in gt_norm:
        return {
            "score": 1.0,
            "exact_match": True
        }

    pairs = [(generated_answer, ground_truth)]
    semantic_score = float(model.predict(pairs)[0])

    return {
        "score": semantic_score,
        "exact_match": semantic_score >= threshold
    }
