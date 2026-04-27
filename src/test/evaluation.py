from __future__ import annotations

from collections import Counter

import mlflow

from .retrieval_metric import precision_at_k, recall_at_k
from .hallucination_check import hallucination_score
from .exact_match import exact_match, load_judge_model
from ..llm.generate import generate_answer


EVAL_SET = [
    {
        "query": "Who directed The Godfather?",
        "relevant_chunks": {"francis ford coppola", "directed", "godfather"},
        "ground_truth": "Francis Ford Coppola directed The Godfather.",
    },
    {
        "query": "What happens at the end of The Shawshank Redemption?",
        "relevant_chunks": {"andy dufresne escapes", "red paroled", "zihuatanejo", "reunion", "pacific ocean"},
        "ground_truth": "Andy Dufresne escapes Shawshank prison through a tunnel, exposes the warden, and reunites with Red on a beach in Zihuatanejo.",
    },
    {
        "query": "How does Fight Club end?",
        "relevant_chunks": {"project mayhem", "narrator shoots himself", "tyler durden", "buildings collapse", "alter ego"},
        "ground_truth": "The narrator shoots himself to kill his alter ego Tyler Durden, and watches Project Mayhem destroy several buildings.",
    },
    {
        "query": "What is the main story of Interstellar?",
        "relevant_chunks": {"wormhole", "nasa", "cooper", "dying earth", "new habitable planet", "black hole", "tesseract"},
        "ground_truth": "A NASA pilot named Cooper travels through a wormhole to find a habitable planet for humanity as Earth dies, eventually entering a black hole and communicating with his daughter across time.",
    },
    {
        "query": "What happens in The Matrix?",
        "relevant_chunks": {"neo", "simulated reality", "red pill", "machines", "the one", "morpheus", "zion"},
        "ground_truth": "Neo discovers that humanity lives in a simulated reality controlled by machines, takes the red pill, and embraces his role as The One to fight for human freedom.",
    },
    {
        "query": "What does Forrest Gump achieve throughout his life?",
        "relevant_chunks": {"vietnam war", "ping pong", "running across america", "shrimping business", "jenny", "football", "medal of honor"},
        "ground_truth": "Forrest Gump inadvertently shapes history by excelling at football, serving heroically in Vietnam, becoming a ping-pong champion, running across America, and building a successful shrimping business.",
    },
    {
        "query": "How does Django get his revenge in Django Unchained?",
        "relevant_chunks": {"django", "kills calvin candie", "rescues broomhilda", "shoots overseers", "blows up plantation", "bounty hunter"},
        "ground_truth": "Django, trained as a bounty hunter by Dr. Schultz, infiltrates Candie's plantation, kills Calvin Candie and his men, and escapes with his wife Broomhilda after blowing up the plantation.",
    },
    {
        "query": "Why does the Joker descend into madness in Joker?",
        "relevant_chunks": {"arthur fleck", "society rejects", "mental illness", "abusive past", "denied medication", "bullied", "thomas wayne"},
        "ground_truth": "Arthur Fleck descends into madness due to a lifetime of social rejection, mental illness, an abusive childhood, loss of medication, and the discovery of his origins tied to Thomas Wayne.",
    },
    {
        "query": "What leads to Jordan Belfort's downfall in The Wolf of Wall Street?",
        "relevant_chunks": {"securities fraud", "pump and dump", "fbi investigation", "informant", "drug addiction", "money laundering", "arrested"},
        "ground_truth": "Jordan Belfort's downfall stems from FBI investigation into his securities fraud and money laundering, compounded by his drug addiction and his decision to become an FBI informant.",
    },
]

def _classify_label(answer: str, em: dict, r_at_5: float, query_type: str) -> str:
    if answer.strip().lower() in {
        "i don't know based on the given context.",
        "i could not find the answer in the provided context.",
        "i don't know.",
    }:
        return "abstained"

    if em["exact_match"] and r_at_5 == 0:
        return "leaked_correct"

    if em["exact_match"] and r_at_5 > 0:
        return "grounded_correct"

    if query_type in {"ending", "explanation"} and r_at_5 > 0:
        return "grounded_correct"

    if not em["exact_match"] and r_at_5 > 0:
        return "retrieved_but_wrong"

    return "wrong_and_unsupported"


def run() -> None:
    judge = load_judge_model()

    p_at_5_list, r_at_5_list, em_list, halluc_list, labels = [], [], [], [], []

    for ex in EVAL_SET:
        query = ex["query"]
        relevant_set = ex["relevant_chunks"]
        ground_truth = ex["ground_truth"]

        result = generate_answer(query)
        answer = result["answer"]
        retrieved_chunks = result["context"]

        query_type = (
            retrieved_chunks[0].get("query_type", "general")
            if retrieved_chunks
            else result.get("query_type", "general")
        )
        movie = result.get("movie", "unknown")

        p_at_5 = precision_at_k(query, retrieved_chunks, judge)
        r_at_5 = recall_at_k(retrieved_chunks, relevant_set, k=5)
        em = exact_match(answer, ground_truth, judge)
        label = _classify_label(answer, em, r_at_5, query_type)
        halluc = hallucination_score(answer, retrieved_chunks, judge, label)

        p_at_5_list.append(p_at_5)
        r_at_5_list.append(r_at_5)
        em_list.append(int(em["exact_match"]))
        halluc_list.append(int(halluc["is_hallucinated"]))
        labels.append(label)

        print(f"\nQuery: {query}")
        print(f"Answer: {answer}")
        print(f"Movie: {movie}")
        print(f"Type: {query_type}")
        print(f"Label: {label}")
        print(f"P@5: {p_at_5:.2f} | R@5: {r_at_5:.2f}")
        print(f"EM: {em['exact_match']} | Hallucination: {halluc['is_hallucinated']}")

    n = len(EVAL_SET)

    print("\n── Aggregate ──")
    print(f"Mean Precision@5: {sum(p_at_5_list)/n:.3f}")
    print(f"Mean Recall@5: {sum(r_at_5_list)/n:.3f}")
    print(f"Exact Match Rate: {sum(em_list)/n:.3f}")
    print(f"Hallucination Rate: {sum(halluc_list)/n:.3f}")
    print(f"Label distribution: {dict(Counter(labels))}")


if __name__ == "__main__":
    run()