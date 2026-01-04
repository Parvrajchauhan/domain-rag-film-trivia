import pandas as pd
from typing import List, Dict
from pathlib import Path
from datetime import datetime

DATA_DIR= Path(__file__).resolve().parent.parent.parent / "data" / "processed"


RETRIEVAL_CHUNK_SIZE = 280
RETRIEVAL_OVERLAP_PCT = 0.10
RETRIEVAL_MIN_LEN = 120



def chunk_document(row: pd.Series) -> List[Dict]:
    text = row["text"]
    parent_doc_id = row["doc_id"]
    section = row["section"]

    if not isinstance(text, str):
        return []

    text = text.strip()
    if len(text) < RETRIEVAL_MIN_LEN:
        return []

    chunk_size = RETRIEVAL_CHUNK_SIZE
    overlap_chars = int(chunk_size * RETRIEVAL_OVERLAP_PCT)

    if overlap_chars >= chunk_size:
        overlap_chars = 0

    chunks = []
    cursor = int(row["start_char"]) if "start_char" in row else 0
    start = 0
    idx = 0
    text_len = len(text)
    RUN_TS = datetime.utcnow().isoformat()

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end].strip()

        if len(chunk) >= RETRIEVAL_MIN_LEN:
            chunks.append({
                "doc_id": parent_doc_id,
                "chunk_id": f"{parent_doc_id}_R{idx + 1:03d}",
                "text": chunk,
                "start_char": cursor + start,
                "end_char": cursor + end,
                "source": row["source"],
                "section": section,
                "title": row["title"],
                "created_at": RUN_TS,
            })
            idx += 1

        next_start = end 
        if next_start <= start:          
            next_start = end

        start = next_start

    return chunks


def main():
    df = pd.read_csv(DATA_DIR / "documents.csv")
    print("Rows in df:", len(df))
    all_chunks = []
    for i, row in df.iterrows():
        all_chunks.extend(chunk_document(row))

    chunks_df = pd.DataFrame(all_chunks)

    out_path = DATA_DIR / "retrieval_chunks.csv"
    chunks_df.to_csv(out_path, index=False)

    print(f"Saved retrieval chunks → {out_path}")
    print(f"Total retrieval chunks: {len(chunks_df)}")


if __name__ == "__main__":
    main()
