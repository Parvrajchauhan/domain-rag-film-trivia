import pandas as pd
from pathlib import Path

DATA_DIR= Path(__file__).resolve().parent.parent.parent / "data" / "processed"

CHUNKS_PATH = Path(DATA_DIR/"chunks.csv")

def main():
    df = pd.read_csv(CHUNKS_PATH)

    print(f"Total chunks: {len(df)}")
    print(f"Total documents: {df['doc_id'].nunique()}")
    print()

    df["chunk_len"] = df["text"].str.len()

    avg_len = df["chunk_len"].mean()
    min_len = df["chunk_len"].min()
    max_len = df["chunk_len"].max()

    print(f"Average chunk length: {avg_len:.1f} chars")
    print(f"Min chunk length: {min_len} chars")
    print(f"Max chunk length: {max_len} chars")
    print()

    short_chunks = df[df["chunk_len"] < 200]
    print("=== SHORT CHUNKS CHECK ===")
    print(f"Chunks < 200 chars: {len(short_chunks)}")
    if len(short_chunks) > 0:
        print(short_chunks[["doc_id", "chunk_id", "chunk_len"]].head())
    print()

    overlap_issues = []

    for doc_id, g in df.sort_values("start_char").groupby("doc_id"):
        prev_end = None
        for _, row in g.iterrows():
            if prev_end is not None:
                if row["start_char"] < prev_end:
                    overlap_issues.append((doc_id, row["chunk_id"]))
            prev_end = row["end_char"]

    if overlap_issues:
        print(f"Overlap detected in {len(overlap_issues)} chunks ")
    else:
        print("No overlap detected")
    print()

    bad_offsets = df[df["end_char"] <= df["start_char"]]
    print(f"Chunks with invalid offsets: {len(bad_offsets)}")
    if len(bad_offsets) > 0:
        print(bad_offsets[["doc_id", "chunk_id", "start_char", "end_char"]].head())
    print()


if __name__ == "__main__":
    main()
