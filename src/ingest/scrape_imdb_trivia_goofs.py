# **IMDb** - Trivia & Goofs (Section-aware, RAG-safe)

import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

INPUT_CSV = DATA_DIR / "movie_catalog/final_catalog.csv"
OUTPUT_CSV = DATA_DIR / "raw/imdb_trivia_goofs.csv"

IMDB_TRIVIA_URL = "https://www.imdb.com/title/{}/trivia/"
IMDB_GOOFS_URL = "https://www.imdb.com/title/{}/goofs/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

SLEEP_RANGE = (1.5, 3.0)
TIMEOUT = 10
MAX_ITEMS = 15


def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        return r.text
    except Exception:
        return None


def extract_trivia(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")

    items = []
    blocks = soup.select("div.ipc-html-content-inner-div")

    for b in blocks:
        text = b.get_text(" ", strip=True)
        if 40 <= len(text) <= 400:
            items.append(text)

    return list(dict.fromkeys(items))[:MAX_ITEMS]


def extract_goofs(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    goofs = {
        "continuity": [],
        "factual_errors": []
    }

    SECTION_MAP = {
        "continuity": "sub-section-continuity",
        "factual_errors": "sub-section-factual_error",
    }

    for key, testid in SECTION_MAP.items():
        container = soup.find("div", {"data-testid": testid})
        if not container:
            continue

        blocks = container.select("div.ipc-html-content-inner-div")
        for b in blocks:
            text = b.get_text(" ", strip=True)
            if 40 <= len(text) <= 400:
                goofs[key].append(text)

    # dedupe + limit
    for k in goofs:
        goofs[k] = list(dict.fromkeys(goofs[k]))[:15]

    return goofs


def main():
    df = pd.read_csv(INPUT_CSV)

    required_cols = {
        "movie_id",
        "movie_title",
        "title_year",
        "movie_imdb_id"
    }

    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")

    rows = []

    for _, row in df.iterrows():
        movie_id = row["movie_id"]
        title = row["movie_title"]
        year = row["title_year"]
        imdb_id = row["movie_imdb_id"]

        print(f"[INFO] {title} ({year})")

        trivia_html = fetch_html(IMDB_TRIVIA_URL.format(imdb_id))
        goofs_html = fetch_html(IMDB_GOOFS_URL.format(imdb_id))

        trivia = extract_trivia(trivia_html) if trivia_html else []

        goofs_continuity = None
        goofs_factual = None

        if goofs_html:
            goofs = extract_goofs(goofs_html)
            goofs_continuity = (
                " || ".join(goofs["continuity"]) if goofs["continuity"] else None
            )
            goofs_factual = (
                " || ".join(goofs["factual_errors"]) if goofs["factual_errors"] else None
            )

        rows.append({
            "movie_id": movie_id,
            "imdb_id": imdb_id,
            "title": title,
            "year": year,
            "trivia": " || ".join(trivia) if trivia else None,
            "goofs_continuity": goofs_continuity,
            "goofs_factual": goofs_factual
        })

        time.sleep(random.uniform(*SLEEP_RANGE))

    if not rows:
        print("[WARN] No data scraped")
        return

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)

    print(f"[DONE] Saved {len(rows)} movies → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
