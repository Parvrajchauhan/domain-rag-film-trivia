from typing import List, Dict


def _min_max_normalize(values: List[float]) -> List[float]:
    min_v = min(values)
    max_v = max(values)

    if max_v == min_v:
        return [1.0] * len(values)

    return [(v - min_v) / (max_v - min_v) for v in values]


def fuse_scores(
    chunks: List[Dict],
    alpha: float = 0.6
) -> List[Dict]:

    if not chunks:
        return []
    
    vector_scores = [float(c.get("score", 0.0)) for c in chunks]
    rerank_scores = [float(c.get("rerank_score", 0.0)) for c in chunks]

    v_norm = _min_max_normalize(vector_scores)
    r_norm = _min_max_normalize(rerank_scores)

    fused = []
    for i, chunk in enumerate(chunks):
        fused_score = alpha * r_norm[i] + (1 - alpha) * v_norm[i]

        fused.append({
            **chunk,
            "final_score": round(float(fused_score), 3),
        })

    fused.sort(key=lambda x: x["final_score"], reverse=True)
    return fused
