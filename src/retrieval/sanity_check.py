import numpy as np
from typing import List, Dict

from src.retrieval.retrieve import retrieve_by_text
from src.retrieval.rerank import rerank
from src.retrieval.scoring import fuse_scores


def sanity_check_retrieval(query: str):
    print("SANITY CHECK: RETRIEVAL")

    results = retrieve_by_text(query, k=10)

    assert results, " No results returned from retrieval"

    print(f"Retrieved {len(results)} chunks")
    print("Top result:")
    r = results[0]
    print(
        f"  score={r['score']:.3f} | "
        f"title={r['title']} | "
        f"section={r['section']}"
    )
    print("\n"+r["text"])


def sanity_check_rerank(query: str):
    print("SANITY CHECK: RERANKING")

    retrieved = retrieve_by_text(query, k=20)
    q_type=retrieved[0].get("query_type", "general")
    reranked = rerank(query, retrieved, query_type=q_type, top_k=10)

    assert reranked, " No results after reranking"

    scores = [c["rerank_score"] for c in reranked]

    assert all(isinstance(s, float) for s in scores), " Invalid rerank scores"

    print(f"Retrieved {len(reranked)} chunks")
    for rank, r in enumerate(reranked, start=1):
            print(f"\nRank {rank}")
            print(f"Score : {r['score']:.3f}")
            print(f"Title : {r['title']}")
            print(f"Chunk : {r['chunk_id']}")
            print(f"Source: {r['source']}")
            print(f"Text  : {r['text']}...")
    top1 = reranked[0]
    assert top1["score"] > 0.3, "Top-1 similarity too low"
    assert all(r["score"] > 0.2 for r in reranked), "Low-similarity noise detected"


def sanity_check_score_fusion(query: str):
    print("SANITY CHECK: SCORE FUSION")

    retrieved = retrieve_by_text(query, k=30)
    q_type=retrieved[0].get("query_type", "general")
    reranked = rerank(query, retrieved, query_type=q_type, top_k=20)
    fused = fuse_scores(reranked, alpha=0.6)

    assert fused, " No results after score fusion"

    scores = [c["final_score"] for c in fused]

    assert all(isinstance(s, float) for s in scores), "Invalid final scores"
    assert scores == sorted(scores, reverse=True), " Final scores not sorted"

    print("Top fused result:")
    r = fused[0]
    print(
        f"  final_score={r['final_score']:.3f} | "
        f"title={r['title']} | "
        f"section={r['section']}"
    )


def sanity_check_metadata_integrity(query: str):
    print("SANITY CHECK: METADATA INTEGRITY")

    results = retrieve_by_text(query, k=5)

    for r in results:
        assert r["doc_id"], "Missing doc_id"
        assert r["chunk_id"], "Missing chunk_id"
        assert isinstance(r["text"], str) and len(r["text"]) > 0, " Empty text"
        assert r["start_char"] < r["end_char"], " Invalid offsets"

    print("Metadata integrity passed")


def sanity_check_no_nan_scores(query: str):
    print("SANITY CHECK: NaN / ZERO VECTORS")

    retrieved = retrieve_by_text(query, k=10)
    q_type=retrieved[0].get("query_type", "general")
    reranked = rerank(query, retrieved, query_type=q_type, top_k=10)
    fused = fuse_scores(reranked)

    for r in fused:
        for key in ["score", "rerank_score", "final_score"]:
            assert not np.isnan(r[key]), f" NaN found in {key}"

    print("No NaNs detected")


def main():
    query = "Who directed the movie Her (2013)?"
    sanity_check_rerank(query)
    print("\n ALL SANITY CHECKS PASSED")


if __name__ == "__main__":
    main()
