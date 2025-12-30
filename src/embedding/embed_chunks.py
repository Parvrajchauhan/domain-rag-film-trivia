import os
import numpy as np
import pandas as pd
from tqdm import tqdm

from .embedding_model import load_embedding_model
from .embedding_cache import EmbeddingCache


BATCH_SIZE = 64
OUTPUT_DIR = "data/embeddings"


REQUIRED_COLUMNS = {
    "doc_id",
    "chunk_id",
    "text",
    "start_char",
    "end_char",
    "source",
    "section",
    "title",
    "created_at",
}


def embed_chunks(chunks_df: pd.DataFrame):

    missing = REQUIRED_COLUMNS - set(chunks_df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    model = load_embedding_model()
    cache = EmbeddingCache()

    texts = chunks_df["text"].tolist()
    embeddings = []

    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Embedding chunks"):
        batch_texts = texts[i : i + BATCH_SIZE]

        batch_embeddings = [None] * len(batch_texts)
        to_encode = []
        encode_positions = []

        for idx, text in enumerate(batch_texts):
            cached = cache.get(text)
            if cached is not None:
                batch_embeddings[idx] = cached
            else:
                to_encode.append(text)
                encode_positions.append(idx)

        if to_encode:
            new_embeddings = model.encode(
                to_encode,
                batch_size=BATCH_SIZE,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            for pos, emb in zip(encode_positions, new_embeddings):
                batch_embeddings[pos] = emb
                cache.set(batch_texts[pos], emb)

        embeddings.extend(batch_embeddings)

    embeddings = np.vstack(embeddings).astype("float32")

    np.save(os.path.join(OUTPUT_DIR, "embeddings.npy"), embeddings)

    meta_df = chunks_df.drop(columns=["text"])
    meta_df.to_parquet(
        os.path.join(OUTPUT_DIR, "chunks_meta.parquet"),
        index=False,
    )

    print(f" Saved {embeddings.shape[0]} embeddings of dim {embeddings.shape[1]}")


if __name__ == "__main__":
    chunks= pd.read_csv("data/processed/chunks.csv")
    embed_chunks(chunks)