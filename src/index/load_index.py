import faiss

INDEX_PATH = "data/index.faiss"


def load_faiss_index():
    index = faiss.read_index(INDEX_PATH)
    return index
