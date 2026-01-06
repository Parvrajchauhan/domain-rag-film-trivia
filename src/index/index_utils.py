import numpy as np
import faiss
import torch
from typing import List, Dict
from ..llm.client import get_llm
from .load_index import load_faiss_index
from .metadata_store import MetadataStore
from ..document.db_save import MetadataStore2
from ..embedding.embedding_model import load_embedding_model

_faiss_index = None
_metadata_store = None
_embedding_model = None
_metadata_store2 =None

def _get_faiss_index():
    global _faiss_index
    if _faiss_index is None:
        _faiss_index = load_faiss_index()
    return _faiss_index
 

def _get_metadata_store():
    global _metadata_store
    if _metadata_store is None:
        _metadata_store = MetadataStore()
    return _metadata_store

def _get_metadata_store2():
    global _metadata_store2
    if _metadata_store2 is None:
        _metadata_store2 = MetadataStore2()
    return _metadata_store2

def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = load_embedding_model()
    return _embedding_model

from typing import List, Dict

def generate_answer(
    prompt: str,
    max_length: int = 128,
    temperature: float = 0.7,
    top_p: float = 0.9
) -> str:

    tokenizer, model = get_llm()

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True
    ).to(model.device)

    with torch.no_grad():
        do_sample = temperature > 0.0

        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=temperature if do_sample else None,
            top_p=top_p if do_sample else None,
            do_sample=do_sample,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = tokenizer.decode(
        output_ids[0],
        skip_special_tokens=True
    )

    if generated.startswith(prompt):
        generated = generated[len(prompt):]

    return generated.strip()



def classify_query_intent_llm(query: str) -> str:

    prompt = f"""
You are helping a movie question-answering system.

Given the following question, do TWO things:
1. Identify the PRIMARY movie being asked about (if any).
2. Classify the intent of the question.

Question:
"{query}"

Choose EXACTLY ONE intent label from:
- plot
- ending
- director
- character
- fact
- explanation
- general

Rules:
- If a movie is clearly mentioned, return its exact title.
- If no specific movie is mentioned, return "unknown".
- Respond in the following STRICT format (no extra text):

movie: <movie title or unknown>
intent: <one label>
"""

    try:
        response = generate_answer(
            prompt,
            max_length=20,
            temperature=0.0
        )
        return response.strip()
    except Exception:
        return "movie: unknown\nintent: general"

def parse_intent_response(response: str) -> tuple[str, str]:
    movie = "unknown"
    intent = "general"

    for line in response.lower().splitlines():
        if line.startswith("movie:"):
            movie = line.replace("movie:", "").strip()
        elif line.startswith("intent:"):
            intent = line.replace("intent:", "").strip()

    valid_intents = {
        "plot", "ending", "director",
        "character", "fact", "explanation", "general"
    }

    if intent not in valid_intents:
        intent = "general"

    return movie, intent


def rewrite_query_by_intent(
    query: str,
    query_type: str,
    movie: str | None = None
) -> str:

    q = query.strip()
    q_lower = q.lower()

    movie = movie.strip().lower() if movie and movie != "unknown" else None

    def anchor(text: str) -> str:
        if movie and movie not in text.lower():
            return f"{movie} {text}"
        return text

    if query_type == "plot":
        if not any(w in q_lower for w in ["plot", "story", "narrative"]):
            return anchor(f"{q} plot story narrative summary")
        return anchor(q)

    if query_type == "ending":
        if not any(w in q_lower for w in ["ending", "end", "final"]):
            return anchor(f"{q} ending final scene conclusion")
        return anchor(q)

    if query_type == "director":
        if not any(w in q_lower for w in ["director", "directed"]):
            return anchor(f"{q} directed by filmmaker director")
        return anchor(q)

    if query_type == "character":
        if not any(w in q_lower for w in ["character", "protagonist"]):
            return anchor(f"{q} character actions role arc")
        return anchor(q)

    if query_type == "fact":
        return anchor(f"{q} movie facts details information")

    if query_type == "explanation":
        return anchor(f"{q} explanation reason process motivation")
    
    if query_type == "general":
        return anchor(q)

    return anchor(q)


def query_index(query_embedding: np.ndarray, k: int = 5) -> List[Dict]:

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    query_embedding = query_embedding.astype("float32")
    faiss.normalize_L2(query_embedding)

    index = _get_faiss_index()
    scores, vector_ids = index.search(query_embedding, k)

    scores = scores[0]
    vector_ids = vector_ids[0].tolist()

    valid = [(vid, score) for vid, score in zip(vector_ids, scores) if vid != -1]
    if not valid:
        return []

    vector_ids, scores = zip(*valid)

    store = _get_metadata_store()
    store2 = _get_metadata_store2()

    vec_rows = store.fetch_by_vector_ids(list(vector_ids))

    vec_by_vid = {}
    doc_ids = set()

    for row in vec_rows:
        vec_by_vid[row.vector_id] = {
            "chunk_id": row.chunk_id,
            "doc_id": row.doc_id,
        }
        doc_ids.add(row.doc_id)

    doc_rows = store2.fetch_by_doc_ids(list(doc_ids))
    doc_by_id = {row.doc_id: row for row in doc_rows}

    results = []

    for vid, score in zip(vector_ids, scores):
        vec = vec_by_vid.get(vid)
        doc = doc_by_id.get(vec["doc_id"]) if vec else None
        if not doc:
            continue

        results.append({
            "score": float(score),
            "vector_id": vid,
            "chunk_id": vec["chunk_id"],
            "doc_id": vec["doc_id"],
            "title": doc.title,
            "text": doc.text,
            "source": doc.source,
            "section": doc.section,
            "start_char": doc.start_char,
            "end_char": doc.end_char,
        })

    return results

def query_text(query: str, k: int = 5) -> List[Dict]:
    
    movie, query_type = parse_intent_response(
    classify_query_intent_llm(query)
)


    rewritten_query = rewrite_query_by_intent(query, query_type,movie)

    model = _get_embedding_model()
    query_embedding = model.encode(
        rewritten_query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    results = query_index(query_embedding, k=k)

    for r in results:
        r["movie"]=movie,
        r["query_type"] = query_type
        r["original_query"] = query
        r["rewritten_query"] = rewritten_query

    return results
