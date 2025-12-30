import numpy as np
import faiss


def query_index(index, query_embedding: np.ndarray, k: int = 5):
    """
    query_embedding: shape (384,)
    returns: (scores, vector_ids)
    """
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    query_embedding = query_embedding.astype("float32")
    faiss.normalize_L2(query_embedding)

    scores, ids = index.search(query_embedding, k)
    return scores[0], ids[0]
