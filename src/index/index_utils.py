import numpy as np
import faiss
from typing import List, Dict

from .load_index import load_faiss_index
from .metadata_store import MetadataStore
from ..embedding.embedding_model import load_embedding_model

_faiss_index = None
_metadata_store = None
_embedding_model = None


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


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = load_embedding_model()
    return _embedding_model


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
    rows = store.fetch_by_vector_ids(list(vector_ids))

    meta_by_id = {row[0]: row for row in rows}

    results = []
    for vid, score in zip(vector_ids, scores):
        row = meta_by_id.get(vid)
        if row is None:
            continue

        (
            vector_id,
            chunk_id,
            doc_id,
            title,
            source,
            start_char,
            end_char,
            text,
        ) = row

        results.append({
            "score": float(score),
            "vector_id": vector_id,
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "title": title,
            "text": text,
            "source": source,
            "start_char": start_char,
            "end_char": end_char,
        })

    return results


def query_text(query: str, k: int = 5) -> List[Dict]:
    
    model = _get_embedding_model()
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return query_index(query_embedding, k=k)
