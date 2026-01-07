import numpy as np
import faiss
from typing import List, Dict
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




def classify_query_intent(query: str) -> str:
    q = query.lower().strip()

    # ENDING
    if any(word in q for word in ["ending", "end", "final", "conclusion", "last scene"]):
        return "ending"

    # DIRECTOR
    if any(word in q for word in ["who directed", "director", "directed by", "filmmaker"]):
        return "director"

    # EXPLANATION (HOW / WHY)
    if q.startswith(("how", "why", "explain")):
        return "explanation"

    # FACT (short factual questions)
    if q.startswith(("who", "when", "where", "which")):
        return "fact"
    
    # CHARACTER
    if any(word in q for word in [
        "character", "protagonist", "antagonist",
        "he", "she", "they", "him", "her"
    ]) and any(word in q for word in ["does", "did", "become", "kill", "betray"]):
        return "character"

    # FACT (metadata-style)
    if any(word in q for word in [
        "release", "year", "runtime", "rating",
        "box office", "budget", "award"
    ]):
        return "fact"

    # PLOT
    if any(word in q for word in [
        "plot", "story", "what happens", "summary"
    ]):
        return "plot"

    # GENERAL fallback
    return "general"


def rewrite_query_by_intent(
    query: str,
    query_type: str,
) -> str:

    q = query.strip()
    q_lower = q.lower()

    if query_type == "plot":
        if not any(w in q_lower for w in ["plot", "story", "narrative"]):
            return f"{q} plot story narrative summary"
        return q

    if query_type == "ending":
        if not any(w in q_lower for w in ["ending", "end", "final"]):
            return f"{q} ending final scene conclusion"
        return q

    if query_type == "director":
        if not any(w in q_lower for w in ["director", "directed"]):
            return f"{q} directed by filmmaker director"
        return q

    if query_type == "character":
        if not any(w in q_lower for w in ["character", "protagonist"]):
            return f"{q} character actions role arc"
        return q

    if query_type == "fact":
        return f"{q} movie facts details information"

    if query_type == "explanation":
        return f"{q} explanation reason process motivation"

    if query_type == "general":
        return q

    return q



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
    
    query_type = classify_query_intent(query)

    rewritten_query = rewrite_query_by_intent(query, query_type)

    model = _get_embedding_model()
    query_embedding = model.encode(
        rewritten_query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    results = query_index(query_embedding, k=k)

    for r in results:
        r["query_type"] = query_type
        r["original_query"] = query
        r["rewritten_query"] = rewritten_query

    return results


