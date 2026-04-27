from .generate import generate_answer


TEST_QUERIES = [
    "Who directed Inception?",
    "Who directed The Godfather?",

    "What happens at the end of The Shawshank Redemption?",
    "How does Fight Club end?",

    "What is the main story of Interstellar?",
    "What happens in The Matrix?",

    "What does Forrest Gump achieve throughout his life?",
    "How does Django get his revenge in Django Unchained?",

    "Why does the Joker descend into madness in Joker?",
    "What leads to Jordan Belfort’s downfall in The Wolf of Wall Street?"
]

def sanity_check_query(query: str):
    print(f"QUERY: {query}")

    result = generate_answer(query)

    answer = result["answer"]
    context = result["context"]

    assert answer, " Empty LLM answer"
    assert len(context) <= 8, " Too many chunks sent to LLM"

    print("\n LLM ANSWER:")
    print(answer)

    print("LLM grounding looks OK")


def run_sanity_checks():
    for q in TEST_QUERIES:
        sanity_check_query(q)

    print("\n ALL SANITY CHECKS PASSED")


if __name__ == "__main__":
    run_sanity_checks()
