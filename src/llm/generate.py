import torch

from .client import get_llm
from .prompt_temp import build_prompt
from .safety import postprocess_answer

from ..retrieval.retrieve import retrieve_by_text
from ..retrieval.rerank import rerank

QUESTION_TOP_K = {
    "fact": 3,       
    "director": 2,   
    "ending": 4,     
    "plot": 8,        
    "character": 5,   
    "explanation": 6, 
    "general": 5,     
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
        base_k=base_k
    )



def generate_answer(
    query: str,
    max_new_tokens: int = 128,
) -> dict:

    retrieved = retrieve_by_text(query, k=15)
    reranked = rerank(query, retrieved, top_k=15)
    q_type = reranked[0].get("query_type", "general")
    query_r = reranked[0].get("rewritten_query") or query
    movie= reranked[0].get("movie") or "unknown"
    reranked = choose_top_k(reranked)


    if not reranked:
        return {
            "answer": "I don't know based on the given context.",
            "context": [],
        }
    
    prompt = build_prompt(query_r, reranked,q_type)

    tokenizer, model = get_llm()

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048,
    )

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

    answer = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    answer = postprocess_answer(answer)

    return {
        "answer": answer,
        "context": reranked,
        "movie":movie,
        "query_type":q_type
    }
