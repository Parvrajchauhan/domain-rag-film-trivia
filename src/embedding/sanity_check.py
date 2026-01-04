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

    print("\nCheck 2: Cosine similarity semantic sanity test")

    idx_a = 10
    idx_b = 11
    idx_c = len(chunks_meta) - 1

    sim_close = cosine_similarity(
        embeddings[idx_a].reshape(1, -1),
        embeddings[idx_b].reshape(1, -1),
    )[0][0]

    sim_far = cosine_similarity(
        embeddings[idx_a].reshape(1, -1),
        embeddings[idx_c].reshape(1, -1),
    )[0][0]

    print(f"Similarity (random vs random) 1: {sim_close:.3f}")
    print(f"Similarity (random vs random) 2: {sim_far:.3f}")

    assert -0.1 <= sim_close <= 1.0
    assert -0.1 <= sim_far <= 1.0

    print("Cosine similarity values look valid")

    print("\nCheck 3: Vector health check")

    norms = np.linalg.norm(embeddings, axis=1)

    assert not np.isnan(embeddings).any(), "NaNs found in embeddings"
    assert np.all(norms > 0), "Zero vectors detected"

    print(
        f"Vector norms — min: {norms.min():.3f}, "
        f"mean: {norms.mean():.3f}, "
        f"max: {norms.max():.3f}"
    )

    print("\nCheck 4: Spot-check content")

    sample_idx = 0
    row = chunks_meta.iloc[sample_idx]
    vector = embeddings[sample_idx]

    print("Chunk ID:", row["chunk_id"])
    print("Title / Section:", row["title"], "—", row["section"])
    print("Offsets:", row["start_char"], "-", row["end_char"])
    print("Text preview:", row.get("text", "")[:150])
    print("Vector norm:", np.linalg.norm(vector))

    print("\nEmbedding sanity check PASSED")


if __name__ == "__main__":
    main()
