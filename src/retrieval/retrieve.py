from typing import List, Dict

from ..index.index_utils import query_text, query_index



def retrieve_by_text(
    query: str,
    k: int = 5
) -> List[Dict]:
    return query_text(query, k=k)

