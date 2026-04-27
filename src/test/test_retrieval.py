from __future__ import annotations

from ..index.index_utils import query_text

TEST_QUERIES = [
    "Who directed Inception?",
    "Who directed The Godfather?",

    "What happens at the end of The Shawshank Redemption?",
    "How does Fight Club end?",]

# Minimum acceptable scores
TOP1_MIN_SCORE  = 0.30
TOPK_MIN_SCORE  = 0.20


def run_tests() -> None:
    print("RETRIEVAL TESTING")
    failures: list[str] = []

    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")

        results = query_text(query, k=5)

        if not results:
            msg = f"No results returned for: '{query}'"
            print(f"  FAIL — {msg}")
            failures.append(msg)
            continue

        for rank, r in enumerate(results, start=1):
            print(f"\n  Rank {rank}")
            print(f"  Score : {r['score']:.3f}")
            print(f"  Title : {r['title']}")
            print(f"  Chunk : {r['chunk_id']}")
            print(f"  Source: {r['source']}")
            print(f"  Text  : {r['text'][:200]}...")

        top1_score = results[0]["score"]
        if top1_score <= TOP1_MIN_SCORE:
            msg = f"Top-1 score too low ({top1_score:.3f}) for: '{query}'"
            print(f"  FAIL — {msg}")
            failures.append(msg)

        low_scores = [r for r in results if r["score"] <= TOPK_MIN_SCORE]
        if low_scores:
            msg = (
                f"{len(low_scores)} chunk(s) below min score threshold "
                f"for: '{query}'"
            )
            print(f"  WARN — {msg}")

    print("\n── Summary ────────────────────────────────────────────────────")
    if failures:
        print(f"FAILED — {len(failures)} issue(s):")
        for f in failures:
            print(f"  - {f}")
        raise AssertionError(f"{len(failures)} retrieval test(s) failed.")
    else:
        print("ALL RETRIEVAL TESTS PASSED")


if __name__ == "__main__":
    run_tests()