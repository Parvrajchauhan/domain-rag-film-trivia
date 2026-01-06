from .generate import generate_answer


TEST_QUERIES = [
    "Who directed Inception?",
    "What happens at the end of Shawshank Redemption?",
    "Which movie features Pandora?",
    
    # Iron Man
    "How does Tony Stark escape captivity in Afghanistan, and what key realization changes him?",
    "What mistake does Tony Stark make that allows Obadiah Stane to nearly succeed?",
    
    # X-Men: First Class
    "What ideological difference causes Charles Xavier and Erik Lehnsherr to part ways?",
    "How does Erik Lehnsherr ultimately kill Sebastian Shaw, and why is this significant?",
    
    # The Wolf of Wall Street
    "What specific illegal practices lead to Jordan Belfort’s downfall?",
    "How does Jordan Belfort manipulate his employees to maintain loyalty during the fraud?",
    
    # Transformers
    "Why are the Autobots searching for the AllSpark, and what happens when it is activated?"
]

def sanity_check_query(query: str):
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")

    result = generate_answer(query, top_k=5)

    answer = result["answer"]
    context = result["context"]

    assert answer, " Empty LLM answer"
    assert len(context) <= 8, " Too many chunks sent to LLM"

    print("\n LLM ANSWER:")
    print(answer)

    if "don't know" not in answer.lower():
        found_overlap = any(
            answer.lower()[:30] in c["text"].lower()
            or any(word in c["text"].lower() for word in answer.lower().split()[:5])
            for c in context
        )
        assert found_overlap, "Possible hallucination detected"

    print("LLM grounding looks OK")


def run_sanity_checks():
    for q in TEST_QUERIES:
        sanity_check_query(q)

    print("\n ALL SANITY CHECKS PASSED")


if __name__ == "__main__":
    run_sanity_checks()
