from .client import generate_answer as groq_generate
from .prompt_temp import build_prompt
from .safety import postprocess_answer

from ..retrieval.retrieve import retrieve_by_text
from ..retrieval.rerank import rerank


QUESTION_TOP_K = {
    "fact": 2,
    "director": 2,
    "ending": 5,
    "plot": 6,
    "character": 5,
    "explanation": 5,
    "general": 5,
    "summary":6
}


def adaptive_top_k(
    reranked_chunks: list[dict],
    base_k: int,
    max_k: int = 8,
    score_drop_threshold: float = 0.25,
):
    if len(reranked_chunks) <= base_k:
        return reranked_chunks

    selected = reranked_chunks[:base_k]
    top_score = selected[0]["rerank_score"]

    for chunk in reranked_chunks[base_k:]:
        if len(selected) >= max_k:
            break

        if top_score - chunk["rerank_score"] <= score_drop_threshold:
            selected.append(chunk)
        else:
            break

    return selected


def choose_top_k(reranked_chunks: list[dict]) -> list[dict]:
    if not reranked_chunks:
        return reranked_chunks

    q_type = reranked_chunks[0].get("query_type", "general")
    base_k = QUESTION_TOP_K.get(q_type, QUESTION_TOP_K["general"])

    return adaptive_top_k(
        reranked_chunks=reranked_chunks,
        base_k=base_k,
    )


def generate_answer(
    query: str,
    max_tokens: int = 256,
) -> dict:

    retrieved = retrieve_by_text(query, k=15)
    q_type = retrieved[0].get("query_type", "general")
    reranked = rerank(query, retrieved, query_type=q_type, top_k=9)

    if not reranked:
        return {
            "answer": "I don't know based on the given context.",
            "context": [],
            "movie": "unknown",
            "query_type": "general",
        }

    query_r = reranked[0].get("rewritten_query") or query
    movie = reranked[0].get("title", "unknown")

    reranked = choose_top_k(reranked)

    prompt = build_prompt(
        query=query_r,
        chunks=reranked,
        query_intent=q_type,
        movie=movie,
    )

    answer = groq_generate(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.2,
    )

    answer = postprocess_answer(answer)

    return {
        "answer": answer,
        "context": reranked,
        "movie": movie,
        "query_type": q_type,
    }
