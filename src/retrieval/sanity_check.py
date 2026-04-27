import numpy as np
from typing import List, Dict

from src.retrieval.retrieve import retrieve_by_text
from src.retrieval.rerank import rerank


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



def main():
    query = "What leads to Jordan Belfort’s downfall in The Wolf of Wall Street?"
    sanity_check_rerank(query)
    print("\n ALL SANITY CHECKS PASSED")


if __name__ == "__main__":
    main()
