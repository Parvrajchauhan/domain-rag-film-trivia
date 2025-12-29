# src/chunking/sentence_splitter.py

SECTION_CHUNK_SIZE = {
    "plot": 1000,
    "synopsis": 1000,
    "trivia": 600,
    "goofs_continuity": 600,
    "goofs_factual": 600,
    "awards_finance": 1200,
}

SECTION_CHUNK_OVERLAP = {
    "plot": 0.15,
    "synopsis": 0.15,
    "trivia": 0.05,
    "goofs_continuity": 0.05,
    "goofs_factual": 0.05,
    "awards_finance": 0.10,
}

OVERLAP_FALLBACK = 100


def get_chunk_size(section: str) -> int:
    return SECTION_CHUNK_SIZE.get(section, 800)


def get_overlap_chars(section: str, chunk_size: int) -> int:
    pct = SECTION_CHUNK_OVERLAP.get(section)
    if pct is None:
        return OVERLAP_FALLBACK
    return int(chunk_size * pct)
