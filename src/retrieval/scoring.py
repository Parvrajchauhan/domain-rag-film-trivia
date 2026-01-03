from typing import List, Dict


def normalize(values):
    min_v = min(values)
    max_v = max(values)

    if max_v == min_v:
        return [1.0 for _ in values]

    return [(v - min_v) / (max_v - min_v) for v in values]


def fuse_scores(
    chunks: List[Dict],
    alpha: float = 0.6
) -> List[Dict]:
    """
    Step 3: Score fusion
    alpha → rerank importance
    (1 - alpha) → vector similarity
    """

    vector_scores = [c["score"] for c in chunks]
    rerank_scores = [c["rerank_score"] for c in chunks]

    v_norm = normalize(vector_scores)
    r_norm = normalize(rerank_scores)

    for i, chunk in enumerate(chunks):
        chunk["final_score"] = round(
            alpha * r_norm[i] + (1 - alpha) * v_norm[i],
            3
        )

    chunks.sort(key=lambda x: x["final_score"], reverse=True)
    return chunks
