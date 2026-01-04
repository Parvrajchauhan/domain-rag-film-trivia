import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"
CHUNKS_PATH = DATA_DIR / "retrieval_chunks.csv"


def main():
    df = pd.read_csv(CHUNKS_PATH)

    print(f"Total retrieval chunks: {len(df)}")
    print(f"Total parent documents: {df['doc_id'].nunique()}")
    print()
    nan_doc_count = df[df["text"].isna()]["chunk_id"].nunique()
    print(f"Documents with NaN text: {nan_doc_count}")

    df["chunk_len"] = df["text"].str.len()

    avg_len = df["chunk_len"].mean()
    min_len = df["chunk_len"].min()
    max_len = df["chunk_len"].max()

    print(f"Average chunk length: {avg_len:.1f} chars")
    print(f"Min chunk length: {min_len} chars")
    print(f"Max chunk length: {max_len} chars")
    print()

    short_chunks = df[df["chunk_len"] < 150]
    print("=== SHORT CHUNKS CHECK ===")
    print(f"Chunks < 150 chars: {len(short_chunks)}")
    if len(short_chunks) > 0:
        print(short_chunks[["chunk_id", "doc_id", "chunk_len"]].head())
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
        print(f"Overlap detected in {len(overlap_issues)} retrieval chunks")
        print(overlap_issues[:5])
    else:
        print("No overlap detected")
    print()

    bad_offsets = df[df["end_char"] <= df["start_char"]]
    print(f"Chunks with invalid offsets: {len(bad_offsets)}")
    if len(bad_offsets) > 0:
        print(bad_offsets[["chunk_id", "start_char", "end_char"]].head())
    print()


if __name__ == "__main__":
    main()
