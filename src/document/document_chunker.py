import pandas as pd
from typing import List, Dict
from pathlib import Path
from datetime import datetime

from .chunk_utils import (
    recursive_split,
    sentence_overlap,
    clean_award_text,
)
from .sentence_splitter import (
    get_chunk_size,
    get_overlap_chars,
)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "inbetween"
OUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_CHUNK_LEN = 120
MAX_DOC_CHUNK_LEN = 800 

def merge_short_chunks(chunks):
    merged = []
    for chunk in chunks:
        if merged and len(chunk["text"]) < MIN_CHUNK_LEN:
            prev = merged[-1]
            prev["text"] += "\n\n" + chunk["text"]
            prev["end_char"] = chunk["end_char"]
        else:
            merged.append(chunk)
    return merged

def chunk_document(row: pd.Series) -> List[Dict]:
    text = row["text"]
    section = row["section"]
    parent_doc_id = row["doc_id"]

    if len(text) > MAX_DOC_CHUNK_LEN:
        text = text[:MAX_DOC_CHUNK_LEN]

    max_chars = get_chunk_size(section)
    overlap_chars = get_overlap_chars(section, max_chars)

    if section == "awards_finance":
        text = clean_award_text(text)

        items = [i.strip() for i in text.split("||") if i.strip()]
        base_chunks = []
        buf = ""

        for item in items:
            if len(buf) + len(item) <= max_chars:
                buf += item + " || "
            else:
                base_chunks.append(buf.strip(" |"))
                buf = item + " || "

        if buf:
            base_chunks.append(buf.strip(" |"))
    else:
        base_chunks = recursive_split(text, max_chars)

    chunks = []
    cursor = int(row["start_char"]) if "start_char" in row else 0

    for i, chunk in enumerate(base_chunks):
        if i > 0 and chunks:
            overlap = sentence_overlap(chunks[-1]["text"], overlap_chars)
            if overlap:
                chunk = overlap + " " + chunk

        if section == "awards_finance":
            chunk = (
                chunk.replace("||", "•")
                     .replace(" • ", "\n• ")
                     .replace("• ", "\n• ")
                     .strip()
            )

        chunk = chunk.strip()
        if len(chunk) < MIN_CHUNK_LEN:
            continue 

        start = cursor
        end = start + len(chunk)

        chunks.append({
            "doc_id": f"{parent_doc_id}_C{i+1:03d}",
            "text": chunk,
            "start_char": int(start),
            "end_char": int(end),
            "source": row["source"],
            "section": section,
            "title": row["title"],
            "created_at": datetime.utcnow().isoformat(),
        })

        cursor = end - overlap_chars if overlap_chars else end

    chunks = merge_short_chunks(chunks)

    return chunks


def main():
    df = pd.read_csv(DATA_DIR / "deduplicated_documents.csv")

    all_chunks = []
    for _, row in df.iterrows():
        all_chunks.extend(chunk_document(row))

    chunks_df = pd.DataFrame(all_chunks)

    out_path = OUT_DIR / "documents.csv"
    chunks_df.to_csv(out_path, index=False)

    print(f"Saved chunks → {out_path}")
    print(f"Total chunks: {len(chunks_df)}")


if __name__ == "__main__":
    main()
