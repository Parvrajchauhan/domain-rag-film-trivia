import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "inbetween"
CHUNKS_PATH = DATA_DIR / "retrieval_chunks.csv"


def main():
    df = pd.read_csv(CHUNKS_PATH)

    print("BASIC STATS ")
    print(f"Total retrieval chunks: {len(df)}")
    print(f"Total parent documents: {df['doc_id'].nunique()}")
    print()

    print(" SECTION DISTRIBUTION ")
    print(df["section"].value_counts())
    print(f"Unique sections: {df['section'].nunique()}")
    print()

    print("NULL CHECKS ")
    print(f"Chunks with NaN text: {df['text'].isna().sum()}")
    print(f"Chunks with empty text: {(df['text'].str.strip() == '').sum()}")
    print()

    df["chunk_len"] = df["text"].str.len()

    print(" LENGTH STATS")
    print(f"Average chunk length: {df['chunk_len'].mean():.1f} chars")
    print(f"Min chunk length: {df['chunk_len'].min()} chars")
    print(f"Max chunk length: {df['chunk_len'].max()} chars")
    print()

    short_chunks = df[df["chunk_len"] < 150]

    print("SHORT CHUNKS CHECK ")
    print(f"Chunks < 150 chars: {len(short_chunks)}")

    if len(short_chunks) > 0:
        print(short_chunks[["chunk_id", "doc_id", "chunk_len"]].head())
    print()

    print("DUPLICATE CHECKS ")

    dup_chunk_ids = df["chunk_id"].duplicated().sum()
    print(f"Duplicate chunk_ids: {dup_chunk_ids}")

    dup_texts = df["text"].duplicated().sum()
    print(f"Duplicate texts: {dup_texts}")
    print()

    print(" CHUNKS PER DOCUMENT ")

    chunks_per_doc = df.groupby("doc_id")["chunk_id"].count()

    print(f"Avg chunks per doc: {chunks_per_doc.mean():.2f}")
    print(f"Min chunks per doc: {chunks_per_doc.min()}")
    print(f"Max chunks per doc: {chunks_per_doc.max()}")
    print()

    print("TITLE CHECK")

    missing_titles = df["title"].isna().sum()
    print(f"Chunks missing title: {missing_titles}")

    title_not_in_text = df[~df["text"].str.startswith("Title:")]
    print(f"Chunks missing 'Title:' prefix: {len(title_not_in_text)}")

    if len(title_not_in_text) > 0:
        print(title_not_in_text[["chunk_id", "doc_id"]].head())
    print()


if __name__ == "__main__":
    main()