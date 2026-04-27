import numpy as np
import faiss
import re
from typing import Optional, Dict,List
from .load_index import load_faiss_index
from .metadata_store import MetadataStore
import  api.core.model_store as model_store
from ..embedding.embedding_model import load_embedding_model
from typing import List, Dict

_faiss_index = None
_metadata_store = None

INTENT_SECTION_FILTERS = {

    "director": {
        "imdb_metadata",
        "lead_section",
        "production"
    },

    "fact": {
        "lead_section",
        "imdb_metadata",
        "reception"
    },

    "summary": {
        "lead_section",
        "imdb_synopsis"
    },

    "plot": {
        "plot_setup",
        "plot_build_up",
        "plot_ending",
        "imdb_synopsis"
    },

    "ending": {
        "plot_ending"
    },

    "explanation": {
        "plot_build_up",
        "plot_ending",
        "production"
    },

    "character": {
        "plot_setup",
        "plot_build_up",
        "plot_ending",
        "imdb_synopsis"
    },

    "general": None
}


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

def classify_query_intent(query: str) -> str:
    q = query.lower().strip()

    # ENDING
    if any(word in q for word in ["ending", "end", "final", "conclusion", "last scene"]):
        return "ending"

    # DIRECTOR
    if any(word in q for word in ["who directed", "director", "directed by", "filmmaker"]):
        return "director"

    # SUMMARY (HIGH-LEVEL, NON-DETAILED)
    if any(word in q for word in [
        "summary", "summarize", "overview",
        "brief", "short summary", "in short"
    ]):
        return "summary"

    # EXPLANATION (HOW / WHY)
    if q.startswith(("how", "why", "explain")):
        return "explanation"

    # FACT (short factual questions)
    if q.startswith(("who", "when", "where", "which")):
        return "fact"

    # CHARACTER ACTIONS
    if any(word in q for word in [
        "character", "protagonist", "antagonist",
        "he", "she", "they", "him", "her"
    ]) and any(word in q for word in [
        "does", "did", "become", "kill", "betray"
    ]):
        return "character"

    # FACT (metadata-style)
    if any(word in q for word in [
        "release", "year", "runtime", "rating",
        "box office", "budget", "award"
    ]):
        return "fact"

    # PLOT (DETAILED EVENTS)
    if any(word in q for word in [
        "plot", "story", "what happens"
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

    # PLOT (detailed events)
    if query_type == "plot":
        if not any(w in q_lower for w in ["plot", "story", "narrative"]):
            return f"{q} plot story narrative events"
        return q

    # ENDING (final resolution)
    if query_type == "ending":
        if not any(w in q_lower for w in ["ending", "end", "final"]):
            return f"{q} ending final scene conclusion"
        return q

    # DIRECTOR (entity lookup)
    if query_type == "director":
        if not any(w in q_lower for w in ["director", "directed"]):
            return f"{q} directed by filmmaker director"
        return q

    # CHARACTER (actions / arc)
    if query_type == "character":
        if not any(w in q_lower for w in ["character", "protagonist"]):
            return f"{q} character actions role arc"
        return q

    # SUMMARY (high-level overview, NOT plot)
    if query_type == "summary":
        if not any(w in q_lower for w in ["summary", "overview", "brief"]):
            return f"{q} summary overview brief"
        return q

    # FACT (metadata / short facts)
    if query_type == "fact":
        return f"{q} movie facts details information"

    # EXPLANATION (how / why)
    if query_type == "explanation":
        return f"{q} explanation reason cause effect"

    # GENERAL fallback
    if query_type == "general":
        return q

    return q


def infer_movie_title_from_results(doc_by_id) -> str | None:
    titles = [doc.title for doc in doc_by_id.values() if doc and doc.title]
    if not titles:
        return None

    return max(set(titles), key=titles.count)


def query_index(
    query_embedding: np.ndarray,
    query_type: str,
    k: int = 5
) -> List[Dict]:

    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    query_embedding = query_embedding.astype("float32")
    faiss.normalize_L2(query_embedding)

    index = _get_faiss_index()

    scores, vector_ids = index.search(query_embedding, k * 3)

    scores = scores[0]
    vector_ids = vector_ids[0].tolist()

    valid = [
        (vid, score)
        for vid, score in zip(vector_ids, scores)
        if vid != -1 and score > 0.2
    ]

    if not valid:
        return []

    vector_ids, scores = zip(*valid)

    store = _get_metadata_store()
    rows = store.fetch_by_vector_ids(list(vector_ids))

    row_by_vid = {row.vector_id: row for row in rows}

    allowed_sections = INTENT_SECTION_FILTERS.get(query_type)

    # Infer dominant movie (for summary)
    require_same_title = query_type == "summary"
    inferred_movie_title = None

    if require_same_title:
        titles = [r.title for r in rows if r and r.title]
        if titles:
            inferred_movie_title = max(set(titles), key=titles.count)

    results = []

    for vid, score in zip(vector_ids, scores):

        row = row_by_vid.get(vid)
        if not row:
            continue

        if allowed_sections is not None:
            section = (row.section or "").lower()
            if section not in allowed_sections:
                continue

        if require_same_title and inferred_movie_title:
            if (row.title or "").lower() != inferred_movie_title.lower():
                continue

        results.append({
            "score": float(score),
            "vector_id": vid,
            "chunk_id": row.chunk_id,
            "doc_id": row.doc_id,
            "title": row.title,
            "text": row.text,
            "source": row.source,
            "section": row.section,
        })

        if len(results) >= k:
            break

    if not results:
        for vid, score in zip(vector_ids, scores):
            row = row_by_vid.get(vid)
            if not row:
                continue

            results.append({
                "score": float(score),
                "vector_id": vid,
                "chunk_id": row.chunk_id,
                "doc_id": row.doc_id,
                "title": row.title,
                "text": row.text,
                "source": row.source,
                "section": row.section,
            })

            if len(results) >= k:
                break

    return results

def query_text(query: str, k: int = 5) -> List[Dict]:
    
    query_type = classify_query_intent(query)

    rewritten_query = rewrite_query_by_intent(query, query_type)

    model =  load_embedding_model()
    if model is None:
        raise RuntimeError("Embedding model not loaded")

    query_embedding = model.encode(
        rewritten_query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    results = query_index(query_embedding, query_type, k=k)

    for r in results:
        r["query_type"] = query_type
        r["original_query"] = query
        r["rewritten_query"] = rewritten_query

    return results


