import os
import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path

BASE_DIR  = Path(__file__).resolve().parent.parent.parent
DATA_DIR  = BASE_DIR / "data" / "inbetween"
OUT_DIR   = DATA_DIR
OUT_FILE  = "deduplicated_documents.csv"
CATALOG_FILE = BASE_DIR / "data" / "catalog.csv"

os.makedirs(OUT_DIR, exist_ok=True)


def sha1(text: str) -> str:
    return hashlib.sha1(text.lower().encode("utf-8")).hexdigest()


IMDB_FIELDS = [
    ("Synopsis", "clean_synopsis"),
    ("Genre", "clean_genre"),
    ("Director", "clean_director"),
    ("Actors", "clean_actors"),
    ("Country", "clean_country"),
    ("Language", "clean_language"),
    ("Awards", "clean_awards"),
]

WIKI_SECTIONS = [
    ("wiki", "lead_section",    "clean_lead_section"),
    ("wiki", "plot_setup",      "clean_plot_setup"),
    ("wiki", "plot_build_up",   "clean_plot_build_up"),
    ("wiki", "plot_ending",     "clean_plot_ending"),
    ("wiki", "production",      "clean_production"),
    ("wiki", "reception",       "clean_reception"),
]


def load_and_merge() -> pd.DataFrame:
    imdb_path = DATA_DIR / "imdb_movies_clean.csv"
    wiki_path = DATA_DIR / "wiki_scrap_clean.csv"

    imdb = pd.read_csv(imdb_path)
    wiki = pd.read_csv(wiki_path)

    merged = pd.merge(wiki, imdb, on="movie_id", how="left")
    if "title_x" in merged.columns or "title_y" in merged.columns:
        merged["title"] = merged.get("title_y").combine_first(merged.get("title_x"))

    return merged


def build_imdb_documents(row) -> list[tuple[str, str]]:
    """
    Returns list of (section, text) for IMDb split into 2 chunks
    """

    docs = []

    synopsis = row.get("clean_synopsis")
    if pd.notna(synopsis) and str(synopsis).strip():
        text = f"Synopsis: {str(synopsis).strip()}"
        docs.append(("imdb_synopsis", text))

    meta_parts = []

    meta_fields = [
        ("Genre", "clean_genre"),
        ("Director", "clean_director"),
        ("Actors", "clean_actors"),
        ("Country", "clean_country"),
        ("Language", "clean_language"),
        ("Awards", "clean_awards"),
    ]

    for label, col in meta_fields:
        val = row.get(col)
        if pd.notna(val) and str(val).strip():
            meta_parts.append(f"{label}: {str(val).strip()}")

    if meta_parts:
        text = ". ".join(meta_parts)
        docs.append(("imdb_metadata", text))

    return docs


def row_to_docs(row: pd.Series, run_ts: str) -> list[dict]:
    docs = []

    year_val = None
    year_raw = row.get("year")
    if pd.notna(year_raw):
        try:
            year_val = int(float(year_raw))
        except Exception:
            pass

    base = {
        "movie_id": row.get("movie_id"),
        "imdb_id":  row.get("imdb_id"),
        "title":    row.get("title"),
        "year":     year_val,
        "imdb_rating": row.get("imdb_rating"),
        "runtime_min": row.get("runtime_min"),
        "wiki_url":    row.get("wiki_url"),
        "created_at":  run_ts,
    }

    imdb_docs = build_imdb_documents(row)

    for section, text in imdb_docs:
        docs.append({
            **base,
            "source": "imdb",
            "section": section,
            "text": text,
            "hash_sha1": sha1(text),
                "text_len": len(text),
        })

    for source, section, col in WIKI_SECTIONS:
        text = row.get(col)
        if pd.notna(text) and str(text).strip():
            text = str(text).strip()
            docs.append({
                **base,
                "source": source,
                "section": section,
                "text": text,
                "hash_sha1": sha1(text),
                "text_len": len(text),
            })

    return docs


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("text_len", ascending=False)
    df = df.drop_duplicates(subset=["hash_sha1"], keep="first")
    df = df.reset_index(drop=True)
    df.insert(0, "doc_id", [f"DOC_{i:06d}" for i in range(1, len(df) + 1)])
    return df


def main():
    run_ts = datetime.utcnow().isoformat()

    print("Loading and merging CSVs…")
    merged = load_and_merge()
    print(f"  Merged rows (wiki only): {len(merged)}")

    print("Collecting documents…")
    records = []
    for _, row in merged.iterrows():
        records.extend(row_to_docs(row, run_ts))
    df = pd.DataFrame(records)
    print(f"  Raw documents: {len(df)}")

    print("Deduplicating…")
    df = deduplicate(df)
    print(f"  After dedupe: {len(df)}")

    FINAL_COLUMNS = [
        "doc_id", "hash_sha1", "text_len",
        "movie_id", "imdb_id",
        "title", "year",
        "imdb_rating", "runtime_min",
        "wiki_url",
        "source", "section",
        "text",
        "created_at",
    ]
    df = df[FINAL_COLUMNS]

    out_path = OUT_DIR / OUT_FILE
    df.to_csv(out_path, index=False)
    print(f"  Saved → {out_path}")

    catalog = (
        df[["doc_id", "movie_id", "title", "year", "source", "section",
            "hash_sha1", "text_len", "created_at"]]
        .rename(columns={
            "hash_sha1":  "sha1",
            "text_len":   "length_chars",
            "created_at": "date_collected",
        })
    )
    catalog.to_csv(CATALOG_FILE, index=False)
    print(f"  Saved → {CATALOG_FILE}")


if __name__ == "__main__":
    main()