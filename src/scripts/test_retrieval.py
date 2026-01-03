from ..index.index_utils import query_text


TEST_QUERIES = [
    "Who directed Inception?",
    "What happens at the end of Shawshank Redemption?",
    "Which movie features Pandora?",
    "what the plot of WALL-E"
]


def run_tests():
    print("RETRIEVAL TESTING")

    for query in TEST_QUERIES:
        print(f"\n Query: {query}")

        results = query_text(query, k=5)

        if not results:
            print(" No results returned")
            continue

        for rank, r in enumerate(results, start=1):
            print(f"\nRank {rank}")
            print(f"Score : {r['score']:.3f}")
            print(f"Title : {r['title']}")
            print(f"Chunk : {r['chunk_id']}")
            print(f"Source: {r['source']}")
            print(f"Text  : {r['text'][:200]}...")

        top1 = results[0]
        assert top1["score"] > 0.3, "Top-1 similarity too low"
        assert all(r["score"] > 0.2 for r in results), "Low-similarity noise detected"

    print("\n Retrieval testing completed successfully")


if __name__ == "__main__":
    run_tests()
