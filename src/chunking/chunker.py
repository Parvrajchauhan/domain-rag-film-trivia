
import pandas as pd
from pathlib import Path
from typing import Dict, List

from .chunk_utils import recursive_split
from .sentence_splitter import get_chunk_size, get_overlap_chars

DATA_DIR = Path(__file__).resolve().parents[2] / "data" 
OUT_PATH = DATA_DIR / "processed"/ "chunks.csv"


def apply_overlap(chunks: List[str], overlap_chars: int) -> List[str]:
    if overlap_chars <= 0:
        return chunks

    overlapped = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            overlapped.append(chunk)
        else:
            prev = overlapped[-1]
            prefix = prev[-overlap_chars:]
            overlapped.append(prefix + chunk)
    return overlapped


def chunk_document(row: pd.Series) -> List[Dict]:
    text = row["text"]
    section = row["section"]
    doc_id = row["doc_id"]

    if not isinstance(text, str) or not text.strip():
        return []

    max_chars = get_chunk_size(section)
    overlap = get_overlap_chars(section, max_chars)

    base_chunks = recursive_split(text, max_chars)
    final_chunks = apply_overlap(base_chunks, overlap)

    results = []
    cursor = 0 

    for idx, chunk_text in enumerate(final_chunks):
        chunk_text = chunk_text.strip()

        if not chunk_text:
            continue

        start_char = cursor
        end_char = start_char + len(chunk_text)

        results.append({
            "doc_id": doc_id,
            "chunk_id": f"{doc_id}_{idx:03d}",
            "text": chunk_text,
            "start_char": start_char,
            "end_char": end_char,
            "source": row["source"],
            "section": section,
            "title": row["title"],
            "created_at": row["created_at"],
        })

        cursor = end_char 

    return results


def main():
    df = pd.read_csv(DATA_DIR / "inbetween/deduplicated_documents.csv")

    all_chunks = []
    for _, row in df.iterrows():
        all_chunks.extend(chunk_document(row))

    chunks_df = pd.DataFrame(all_chunks)
    chunks_df.to_csv(OUT_PATH, index=False)

    print(f"Saved chunks → {OUT_PATH}")
    print(f"Total chunks: {len(chunks_df)}")


if __name__ == "__main__":
    main()
