from .retrieval_metric import precision_at_k, recall_at_k
from .hallucination_check import hallucination_score
from .exact_match import exact_match, load_judge_model
from ..llm.generate import generate_answer


EVAL_SET = [
    {
        "query": "Who directed Inception?",
        "relevant_chunks": {"christopher nolan", "directed"},
        "ground_truth": "Christopher Nolan"
    },
    {
        "query": "What happens at the end of Shawshank Redemption?",
        "relevant_chunks": {
            "andy dufresne escapes",
            "red meets andy",
            "zihuatanejo",
            "parole"
        },
        "ground_truth": "Andy escapes prison and reunites with Red in Zihuatanejo."
    },
    {
        "query": "Which movie features Pandora?",
        "relevant_chunks": {
            "pandora",
            "na'vi",
            "avatar",
            "james cameron"
        },
        "ground_truth": "Avatar"
    },
    {
        "query": "How does Tony Stark escape captivity in Afghanistan, and what key realization changes him?",
        "relevant_chunks": {
            "mark i armor",
            "escapes captivity",
            "weapons responsibility",
            "stops weapons manufacturing"
        },
        "ground_truth": (
            "Tony Stark escapes using the Mark I armor and "
            "realizes his weapons are causing harm."
        )
    },
    {
        "query": "What mistake does Tony Stark make that allows Obadiah Stane to nearly succeed?",
        "relevant_chunks": {
            "arc reactor",
            "trusts obadiah stane",
            "stolen arc reactor",
            "iron monger"
        },
        "ground_truth": (
            "Tony trusts Obadiah Stane, allowing him to steal the arc reactor."
        )
    },
    {
        "query": "What ideological difference causes Charles Xavier and Erik Lehnsherr to part ways?",
        "relevant_chunks": {
            "coexistence",
            "mutant superiority",
            "peaceful coexistence",
            "humans vs mutants"
        },
        "ground_truth": (
            "Charles believes in peaceful coexistence, while Erik believes "
            "mutants should dominate humans."
        )
    },
    {
        "query": "How does Erik Lehnsherr ultimately kill Sebastian Shaw, and why is this significant?",
        "relevant_chunks": {
            "coin through head",
            "magnetic powers",
            "revenge",
            "embraces magneto identity"
        },
        "ground_truth": (
            "Erik kills Shaw by driving a coin through his head, fully embracing "
            "his Magneto identity."
        )
    },
    {
        "query": "What specific illegal practices lead to Jordan Belfort’s downfall?",
        "relevant_chunks": {
            "stock manipulation",
            "pump and dump",
            "securities fraud",
            "money laundering"
        },
        "ground_truth": (
            "Jordan Belfort’s downfall is caused by securities fraud, "
            "pump-and-dump schemes, and money laundering."
        )
    },
    {
        "query": "How does Jordan Belfort manipulate his employees to maintain loyalty during the fraud?",
        "relevant_chunks": {
            "lavish lifestyle",
            "motivational speeches",
            "financial incentives",
            "cult-like loyalty"
        },
        "ground_truth": (
            "He manipulates employees through money, drugs, and motivational "
            "speeches to create loyalty."
        )
    },
    {
        "query": "Why are the Autobots searching for the AllSpark, and what happens when it is activated?",
        "relevant_chunks": {
            "allspark",
            "create transformers",
            "destruction",
            "cybertron"
        },
        "ground_truth": (
            "The Autobots seek the AllSpark because it creates life, but "
            "activating it causes massive destruction."
        )
    }
]


def run():
    judge = load_judge_model()

    for ex in EVAL_SET:
        query = ex["query"]
        relevant = ex["relevant_chunks"]
        ground_truth = ex["ground_truth"]

        result = generate_answer(query)
        answer = result["answer"]
        retrieved_chunks = result["context"] 
        movie=result["movie"]
        query_type=result["query_type"]

        p_at_5 = precision_at_k(query, retrieved_chunks, judge)
        r_at_5 = recall_at_k(retrieved_chunks, relevant, k=5)
        halluc = hallucination_score(answer, retrieved_chunks, judge)
        em = exact_match(answer, ground_truth, judge)

        print("=" * 60)
        print(f"Query: {query}")
        print(f"Answer: {answer}")
        print(f"movie: {movie}")
        print(f"query_type: {query_type}")
        print(f"Precision@5: {p_at_5:.2f}")
        print(f"Recall@5: {r_at_5:.2f}")
        print(f"Hallucination Score: {halluc['score']:.2f}")
        print(f"Is Hallucinated: {halluc['is_hallucinated']}")
        print(f"Exact Match: {em}")


if __name__ == "__main__":
    run()
