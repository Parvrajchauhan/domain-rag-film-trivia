import pandas as pd
import re
from typing import List, Dict
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "inbetween"

RETRIEVAL_CHUNK_SIZE = 1200       # ~300 tokens
RETRIEVAL_OVERLAP_PCT = 0.15      # 15%
RETRIEVAL_MIN_LEN = 120


import re
from typing import List

def split_into_sentences(text: str, min_len: int = 20) -> List[str]:

    raw_sentences = re.split(r'(?<=[.!?])\s+', text)

    sentences = []
    buffer = ""

    for s in raw_sentences:
        s = s.strip()
        if not s:
            continue

        if len(s) < min_len:
            if sentences:
                sentences[-1] += " " + s
            else:
                buffer += " " + s
        else:
            if buffer:
                s = buffer.strip() + " " + s
                buffer = ""
            sentences.append(s)

    if buffer and sentences:
        sentences[-1] += " " + buffer.strip()

    return sentences

def chunk_document(row: pd.Series) -> List[Dict]:
    text = row.get("text", "")
    parent_doc_id = row.get("doc_id", "")
    section = row.get("section", "")
    source = row.get("source", "")
    title = row.get("title", "")

    if not isinstance(text, str):
        return []

    text = text.strip()
    if len(text) < RETRIEVAL_MIN_LEN:
        return []

    sentences = split_into_sentences(text)

    chunk_size = RETRIEVAL_CHUNK_SIZE
    overlap_sent_count = 2  

    chunks = []
    idx = 0
    RUN_TS = datetime.utcnow().isoformat()

    current_chunk = []
    current_len = 0

    for sentence in sentences:
        sent_len = len(sentence)

        if current_len + sent_len > chunk_size and current_chunk:
            chunk_text = " ".join(current_chunk).strip()

            if len(chunk_text) >= RETRIEVAL_MIN_LEN:
                
                final_text = f"Title: {title}\nSection: {section}\n{chunk_text}"if title else chunk_text

                chunks.append({
                    "doc_id": parent_doc_id,
                    "chunk_id": f"{parent_doc_id}_R{idx + 1:03d}",
                    "text": final_text,
                    "source": source,
                    "section": section,
                    "title": title,
                    "created_at": RUN_TS,
                })
                idx += 1

            overlap_sentences = current_chunk[-overlap_sent_count:]
            current_chunk = overlap_sentences.copy()
            current_len = sum(len(s) for s in current_chunk)

        current_chunk.append(sentence)
        current_len += sent_len

    if current_chunk:
        chunk_text = " ".join(current_chunk).strip()
        if len(chunk_text) >= RETRIEVAL_MIN_LEN:
            final_text = f"Title: {title}\nSection: {section}\n{chunk_text}"if title else chunk_text

            chunks.append({
                "doc_id": parent_doc_id,
                "chunk_id": f"{parent_doc_id}_R{idx + 1:03d}",
                "text": final_text,
                "source": source,
                "section": section,
                "title": title,
                "created_at": RUN_TS,
            })

    return chunks


def main():
    df = pd.read_csv(DATA_DIR / "deduplicated_documents.csv")
    print("Rows in df:", len(df))

    all_chunks = []

    for _, row in df.iterrows():
        chunks = chunk_document(row)
        all_chunks.extend(chunks)

    chunks_df = pd.DataFrame(all_chunks)

    out_path = DATA_DIR / "retrieval_chunks.csv"
    chunks_df.to_csv(out_path, index=False)

    print(f"Saved retrieval chunks → {out_path}")
    print(f"Total retrieval chunks: {len(chunks_df)}")


if __name__ == "__main__":
    main()