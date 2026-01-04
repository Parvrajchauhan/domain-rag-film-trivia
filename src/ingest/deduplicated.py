import os
import glob
import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "inbetween"
OUT_DIR_CAT=Path(__file__).resolve().parent.parent.parent / "data"
OUT_DIR = DATA_DIR
OUT_FILE = "deduplicated_documents.csv"
CATALOG_FILE = "catalog.csv"

os.makedirs(OUT_DIR, exist_ok=True)

def sha1(text: str) -> str:
    return hashlib.sha1(text.lower().encode("utf-8")).hexdigest()

def load_excluded_movie_ids():
    path = os.path.join(DATA_DIR, "wiki_missing_clean.csv")
    if not os.path.exists(path):
        return set()

    df = pd.read_csv(path)
    if "movie_id" not in df.columns:
        return set()

    return set(df["movie_id"].dropna().astype(int))

def build_awards_finance_text(row):
    parts = []

    mapping = {
        "award_wins": "Award wins",
        "award_nominations": "Award nominations",
        "budget": "Budget",
        "opening_weekend_us_canada": "Opening weekend US/Canada",
        "gross_us_canada": "Gross US/Canada",
        "gross_worldwide": "Gross worldwide",
    }

    for col, label in mapping.items():
        val = row.get(col)
        if pd.notna(val):
            parts.append(f"{label}: {val}")

    return ". ".join(parts)


WIKI_SECTION_MAP = ["lead_section", "plot_setup","plot_build_up","plot_ending","production","reception"]

def collect_documents():
    rows = []
    exclude_movie_ids = load_excluded_movie_ids()

    files = [
        f for f in glob.glob(os.path.join(DATA_DIR, "*_clean.csv"))
        if os.path.basename(f) != "wiki_missing_clean.csv"
    ]

    RUN_TS = datetime.utcnow().isoformat()

    for path in files:
        df = pd.read_csv(path)
        filename = os.path.basename(path)

        for _, row in df.iterrows():

            year_raw = row.get("year")
            if pd.notna(year_raw):
                try:
                    year_val = int(float(year_raw))
                except Exception:
                    year_val = None
            else:
                year_val = None

            movie_id = row.get("movie_id")
            if pd.notna(movie_id) and int(movie_id) in exclude_movie_ids:
                continue

            base_meta = {
                "movie_id": row.get("movie_id"),
                "imdb_id": row.get("imdb_id"),
                "title": row.get("title"),
                "year": year_val,
                "created_at": RUN_TS,
            }

            for section in ["synopsis", "summaries"]:
                clean_col = f"clean_{section}"
                if clean_col in df.columns and pd.notna(row.get(clean_col)):
                    text = row[clean_col]
                    rows.append({
                        **base_meta,
                        "source": "imdb",
                        "section": section,
                        "text": text,
                        "hash_sha1": sha1(text),
                        "text_len": len(text),
                    })

            for section in ["trivia", "goofs_continuity", "goofs_factual"]:
                clean_col = f"clean_{section}"
                if clean_col in df.columns and pd.notna(row.get(clean_col)):
                    text = row[clean_col]
                    rows.append({
                        **base_meta,
                        "source": "imdb",
                        "section": section,
                        "text": text,
                        "hash_sha1": sha1(text),
                        "text_len": len(text),
                    })

            if filename == "imdb_awards_boxoffice_clean.csv":
                text = build_awards_finance_text(row)
                if text:
                    rows.append({
                        **base_meta,
                        "source": "imdb",
                        "section": "awards_finance",
                        "text": text,
                        "hash_sha1": sha1(text),
                        "text_len": len(text),
                    })

            for section in WIKI_SECTION_MAP:
                clean_col = f"clean_{section}"
                if clean_col in df.columns and pd.notna(row.get(clean_col)):
                    text = row[clean_col]
                    rows.append({
                        **base_meta,
                        "source": "wiki",
                        "section": section,
                        "text": text,
                        "hash_sha1": sha1(text),
                        "text_len": len(text),
                    })

    return pd.DataFrame(rows)


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("text_len", ascending=False)
    df = df.drop_duplicates(subset=["hash_sha1"], keep="first")
    df = df.reset_index(drop=True)

    df.insert(0, "doc_id", [f"DOC_{i:06d}" for i in range(1, len(df) + 1)])
    return df

def main():
    print("Collecting documents")
    df = collect_documents()
    print(f"Collected: {len(df)} rows")

    print("Deduplicating")
    df = deduplicate(df)
    print(f"After dedupe: {len(df)} documents")

    FINAL_COLUMNS = [
        "doc_id", "hash_sha1", "text_len",
        "movie_id", "imdb_id", 
        "title", "year",
        "source", "section",
        "text", "created_at"
    ]
    df = df[FINAL_COLUMNS]

    out_path = os.path.join(OUT_DIR, OUT_FILE)
    df.to_csv(out_path, index=False)
    print(f"Saved → {out_path}")

    catalog = df[[
        "doc_id",
        "title",
        "source",
        "hash_sha1",
        "text_len",
        "created_at"
    ]].rename(columns={
        "hash_sha1": "sha1",
        "text_len": "length_chars",
        "created_at": "date_collected"
    })

    catalog_path = os.path.join(OUT_DIR_CAT, CATALOG_FILE)
    catalog.to_csv(catalog_path, index=False)
    print(f"Saved → {catalog_path}")

if __name__ == "__main__":
    main()
