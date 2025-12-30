SECTION_CHUNK_SIZES = {
    "plot": 1200,
    "production": 1000,
    "reception": 1000,
    "synopsis": 900,
    "summaries": 900,
    "trivia": 800,
    "goofs_continuity": 700,
    "goofs_factual": 700,
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


DEFAULT_OVERLAP = 0.10


def get_chunk_size(section: str) -> int:
    return SECTION_CHUNK_SIZES.get(section, 800)


def get_overlap_chars(section: str, chunk_size: int) -> int:
    pct = SECTION_CHUNK_OVERLAP.get(section, DEFAULT_OVERLAP)
    return int(chunk_size * pct)
