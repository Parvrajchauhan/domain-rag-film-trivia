from sentence_transformers import SentenceTransformer


def load_embedding_model(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    device: str | None = None,
):
    return SentenceTransformer(model_name, device=device)
