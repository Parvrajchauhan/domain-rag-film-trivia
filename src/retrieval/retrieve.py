from typing import List, Dict

from ..index.index_utils import query_text, query_index



def retrieve_by_text(
    query: str,
    k: int = 5
) -> List[Dict]:
    return query_text(query, k=k)


def retrieve_by_embedding(
    query_embedding,
    k: int = 5
) -> List[Dict]:
    return query_index(query_embedding, k=k)
