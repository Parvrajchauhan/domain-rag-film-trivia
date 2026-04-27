from collections import Counter

from .client import generate_answer as groq_generate
from .prompt_temp import build_prompt
from .safety import postprocess_answer

from ..retrieval.retrieve import retrieve_by_text
from ..retrieval.rerank import rerank
from .filter_chunks import filter_supported_chunks


QUESTION_TOP_K = {
    "fact": 2,
    "director": 2,
    "ending": 5,
    "plot": 6,
    "character": 5,
    "explanation": 5,
    "general": 5,
    "summary": 6,
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

    #  STEP 1: Retrieve
    retrieved = retrieve_by_text(query, k=15)

    if not retrieved:
        return {
            "answer": "I could not find relevant information.",
            "context": [],
            "movie": "unknown",
            "query_type": "general",
        }
        
    #  STEP 2: Robust query type detection
    types = [c.get("query_type", "general") for c in retrieved]
    q_type = Counter(types).most_common(1)[0][0]

    #  STEP 3: Rerank
    reranked = rerank(query, retrieved, query_type=q_type, top_k=9)

    if not reranked:
        return {
            "answer": "I don't know based on the given context.",
            "context": [],
            "movie": "unknown",
            "query_type": q_type,
        }

    #  STEP 4: Compute movie scores
    movie_scores = {}
    for c in reranked:
        title = c.get("title")
        score = c.get("rerank_score", 0.0)

        if not title:
            continue

        movie_scores[title] = movie_scores.get(title, 0.0) + score

    #  STEP 5: Pick best movie
    movie = max(movie_scores, key=movie_scores.get) if movie_scores else "unknown"

    #  STEP 6: Override with extracted movie (if available)
    extracted_movie = reranked[0].get("extracted_movie")
    if extracted_movie:
        movie = extracted_movie

    #  STEP 7: Ambiguity check (score-based)
    sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)

    if len(sorted_movies) > 1:
        top_score = sorted_movies[0][1]
        second_score = sorted_movies[1][1]

        if second_score / top_score > 0.75:
            return {
                "answer": "This query is ambiguous. Please specify the movie more clearly.",
                "context": [],
                "movie": "unknown",
                "query_type": "general",
            }

    #  STEP 8: Enforce movie consistency
    reranked = [c for c in reranked if c.get("title") == movie]

    if not reranked:
        return {
            "answer": "I could not find consistent information for a single movie.",
            "context": [],
            "movie": "unknown",
            "query_type": q_type,
        }

    #  STEP 9: Weak confidence fallback
    if reranked[0]["rerank_score"] < 0.2:
        return {
            "answer": "I could not find a confident answer in the provided context.",
            "context": [],
            "movie": "unknown",
            "query_type": q_type,
        }

    #  STEP 10: Adaptive top-k selection
    reranked = choose_top_k(reranked)

    #  STEP 11: Build prompt
    query_r = reranked[0].get("rewritten_query") or query

    prompt = build_prompt(
        query=query_r,
        chunks=reranked,
        query_intent=q_type,
        movie=movie,
    )

    #  STEP 12: Generate answer (lower temp for factual queries)
    temperature = 0.05 if q_type in ["fact", "director"] else 0.2

    answer = groq_generate(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    #  STEP 13: Postprocess
    answer = postprocess_answer(answer)

    #  STEP 14: Filter supported chunks
    final_context = filter_supported_chunks(
        answer=answer,
        chunks=reranked,
        query_type=q_type,
        sim_threshold=0.55,
    )

    return {
        "answer": answer,
        "context": final_context or [],
        "context_raw": reranked,
        "movie": movie,
        "query_type": q_type,
    }