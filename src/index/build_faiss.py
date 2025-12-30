import os
import faiss
import numpy as np

EMBEDDINGS_PATH = "data/embeddings/embeddings.npy"
INDEX_PATH = "data/index.faiss"


def main():
    print("Loading embeddings...")
    embeddings = np.load(EMBEDDINGS_PATH)

    assert embeddings.dtype == np.float32
    assert embeddings.ndim == 2
    assert embeddings.shape[1] == 384

    print(f"Loaded embeddings: {embeddings.shape}")

    print("Normalizing embeddings (L2)")
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)

    index.add(embeddings)
    assert index.ntotal == embeddings.shape[0]

    os.makedirs("data", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    print(f"FAISS index built & saved to {INDEX_PATH}")
    print(f"Total vectors indexed: {index.ntotal}")


if __name__ == "__main__":
    main()
