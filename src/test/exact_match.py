from sentence_transformers import CrossEncoder

def load_judge_model():
    return CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

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

    pairs = [(generated_answer, ground_truth)]
    score = float(model.predict(pairs)[0])

    return {
        "score": score,
        "exact_match": score >= threshold
    }

