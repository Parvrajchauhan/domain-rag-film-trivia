from src.llm.generate import generate_answer
from .evaluation import hallucination_score,compute_confidence
import time
from fastapi import  HTTPException

import concurrent.futures

EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)

def run_with_timeout(fn, timeout=16):
    future = EXECUTOR.submit(fn)
    try:
        return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail={
                "error": "TIMEOUT",
                "message": "Request exceeded time limit."
            }
        )
    

def build_citations(chunks: list[dict]) -> list[dict]:
    citations = []

    for c in chunks:
        score = min( c.get("rerank_score", c.get("base_similarity", 0.0)), 1.0)

        citations.append({
            "id": c["chunk_id"],
            "title": c["title"],
            "source": c["source"],
            "section": c["section"].replace("_", " ").title(),
            "snippet": c["text"][:200],
            "score": score
        })

    return citations

ABSTENTION_ANSWERS = {
    "i don't know.",
    "i don't know based on the given context.",
    "not enough information in the context."
}

def handle_abstention(answer: str):
    return answer.strip().lower() in ABSTENTION_ANSWERS

def validate_retrieval(chunks: list[dict]):
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "EMPTY_RETRIEVAL",
                "message": "No relevant context found for the query."
            }
        )


def generate(query: str,judge):
    start = time.perf_counter()
    answer= run_with_timeout(lambda: generate_answer(query))
    ans = answer["answer"]
    retrieved_chunks = answer["context"]
    if handle_abstention(ans):
        return {
            "answer": answer,
            "sources": [],
            "hallucination_score": 1.0,
            "confidence": 0.0,
            "latency_ms": 0
        }

    validate_retrieval(retrieved_chunks)
    result=hallucination_score(ans,retrieved_chunks,judge)
    latency_ms = (time.perf_counter() - start) * 1000
    sources=build_citations(retrieved_chunks)

    confidence=compute_confidence(retrieved_chunks,result["score"])
    return{
      "answer": ans,
      "sources": sources,
      "hallucination_score": result["score"],
      "confidence": confidence,
      "latency_ms": latency_ms
    }
