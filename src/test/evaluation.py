from .retrieval_metric import precision_at_k, recall_at_k
from .hallucination_check import hallucination_score
from .exact_match import exact_match, load_judge_model
from ..llm.generate import generate_answer

import mlflow
from collections import Counter

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

    mlflow.set_experiment("film_rag_evaluation")
    mlflow.set_tracking_uri("http://127.0.0.1:5000")

    p_at_5_list = []
    r_at_5_list = []
    em_list = []
    halluc_list = []
    labels = []

    with mlflow.start_run(run_name="rag_eval_v1"):

        mlflow.log_param("retriever", "faiss + embedding")
        mlflow.log_param("reranker", "intent-aware rerank")
        mlflow.log_param("hallucination_judge", "cross-encoder")
        mlflow.log_param("intent_classifier", "heuristic")

        for ex in EVAL_SET:
            query = ex["query"]
            relevant = ex["relevant_chunks"]
            ground_truth = ex["ground_truth"]

            result = generate_answer(query)
            answer = result["answer"]
            retrieved_chunks = result["context"]

            movie = result.get("movie", "unknown")
            query_type = result.get("query_type", "general")

            p_at_5 = precision_at_k(query, retrieved_chunks, judge)
            r_at_5 = recall_at_k(retrieved_chunks, relevant, k=5)
            em = exact_match(answer, ground_truth, judge)

            query_type = (
                retrieved_chunks[0].get("query_type", "general")
                if retrieved_chunks else "general"
            )

            if answer.strip() == "I don't know based on the given context.":
                label = "abstained"

            elif query_type in {"ending", "explanation"} and r_at_5 > 0:
                label = "grounded_correct"

            elif em and r_at_5 == 0:
                label = "leaked_correct"

            elif em and r_at_5 > 0:
                label = "grounded_correct"

            elif not em and r_at_5 > 0:
                label = "retrieved_but_wrong"

            else:
                label = "wrong_and_unsupported"

            halluc = hallucination_score(
                answer,
                retrieved_chunks,
                judge,
                label
            )

            mlflow.log_metric("precision_at_5", p_at_5)
            mlflow.log_metric("recall_at_5", r_at_5)
            mlflow.log_metric("exact_match", em["score"])
            mlflow.log_metric("exact_match", int(em["exact_match"]))
            mlflow.log_metric("hallucination_score", halluc["score"])
            mlflow.log_metric("is_hallucinated", int(halluc["is_hallucinated"]))

            mlflow.set_tag("query_intent", query_type)
            mlflow.set_tag("label", label)
            mlflow.set_tag("movie", movie)

            p_at_5_list.append(p_at_5)
            r_at_5_list.append(r_at_5)
            em_list.append(int(em["exact_match"]))
            halluc_list.append(int(halluc["is_hallucinated"]))
            labels.append(label)
            
            print("\n")
            print(f"Query: {query}")
            print(f"Answer: {answer}")
            print(f"movie: {movie}")
            print(f"query_type: {query_type}")
            print(f"Precision@5: {p_at_5:.2f}")
            print(f"Recall@5: {r_at_5:.2f}")
            print(f"label: {label}")
            print(f"Hallucination Score: {halluc['score']:.2f}")
            print(f"Is Hallucinated: {halluc['is_hallucinated']}")
            print(f"Exact Match: {em}")

        mlflow.log_metric("mean_precision_at_5", sum(p_at_5_list) / len(p_at_5_list))
        mlflow.log_metric("mean_recall_at_5", sum(r_at_5_list) / len(r_at_5_list))
        mlflow.log_metric("exact_match_rate", sum(em_list) / len(em_list))
        mlflow.log_metric("hallucination_rate", sum(halluc_list) / len(halluc_list))

        label_counts = Counter(labels)
        for k, v in label_counts.items():
            mlflow.log_metric(f"label_count_{k}", v)


if __name__ == "__main__":
    run()