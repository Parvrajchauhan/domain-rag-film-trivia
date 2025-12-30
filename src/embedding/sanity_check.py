import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


EMBEDDINGS_PATH = "data/embeddings/embeddings.npy"
META_PATH = "data/embeddings/chunks_meta.parquet"


def main():
    print("Loading artifacts...")
    embeddings = np.load(EMBEDDINGS_PATH)
    chunks_meta = pd.read_parquet(META_PATH)

    assert embeddings.shape[0] == len(chunks_meta), (
        f"Mismatch: embeddings={embeddings.shape[0]}, "
        f"metadata={len(chunks_meta)}"
    )
    assert embeddings.shape[1] == 384, (
        f"Expected 384-dim vectors, got {embeddings.shape[1]}"
    )

    print("Shape validation passed")


    print("\nCheck 2: Cosine similarity sanity test")
    TARGET_DOC_ID = "DOC_000010"   

    same_movie_chunks = chunks_meta[
        chunks_meta["doc_id"] == TARGET_DOC_ID
    ].index[:2]

    assert len(same_movie_chunks) == 2, "Not enough chunks for selected movie"

    idx_a, idx_b = same_movie_chunks

    sim_same = cosine_similarity(
        embeddings[idx_a].reshape(1, -1),
        embeddings[idx_b].reshape(1, -1),
    )[0][0]

    diff_chunk = chunks_meta[
        chunks_meta["doc_id"] != TARGET_DOC_ID
    ].index[0]

    sim_diff = cosine_similarity(
        embeddings[idx_a].reshape(1, -1),
        embeddings[diff_chunk].reshape(1, -1),
    )[0][0]

    print(f"Same movie similarity     : {sim_same:.3f}")
    print(f"Different movie similarity: {sim_diff:.3f}")

    assert sim_same > sim_diff, "Cosine sanity check failed"
    print("Cosine similarity sanity passed")


    print("\n Check 3: Spot-check content")

    sample_idx = 0
    row = chunks_meta.iloc[sample_idx]
    vector = embeddings[sample_idx]

    print("\nChunk ID:", row["chunk_id"])
    print("Text preview:", row["title"], "—", row["section"])
    print("First 150 chars:", "\n", row["start_char"], "-", row["end_char"])
    print("Vector norm:", np.linalg.norm(vector))

    assert not np.isnan(vector).any(), "NaNs found in embedding"
    assert np.linalg.norm(vector) > 0, "Zero vector detected"



if __name__ == "__main__":
    main()
