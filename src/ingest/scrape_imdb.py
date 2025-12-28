# **IMDb** - Plot, year, director, genre, runtime
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" 

INPUT_CSV = DATA_DIR /"movie_catalog/final_catalog.csv"
OUTPUT_CSV = DATA_DIR /"raw/imdb_movies.csv"

IMDB_PLOT_URL = "https://www.imdb.com/title/{}/plotsummary/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

SLEEP_RANGE = (1.5, 3.0)
TIMEOUT = 10

def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"[WARN] {url} status={r.status_code}")
            return None
        return r.text
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return None



def parse_plot_page(html: str):
    soup = BeautifulSoup(html, "html.parser")

    blocks = soup.select("div.ipc-html-content-inner-div")
    texts = [b.get_text(strip=True) for b in blocks if len(b.get_text(strip=True)) > 50]

    # Longest block = synopsis
    synopsis = max(texts, key=len) if texts else None

    # Summaries = short unique blocks
    summaries = []
    for t in texts:
        if synopsis and t == synopsis:
            continue
        if 80 <= len(t) <= 400:
            summaries.append(t)

    summaries = list(dict.fromkeys(summaries))  # dedupe
    summaries_text = " || ".join(summaries[:5]) if summaries else None

    return synopsis, summaries_text



def main():
    df = pd.read_csv(INPUT_CSV)

    required_cols = {"movie_id","movie_title","title_year","movie_imdb_id"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")

    rows = []

    for _, row in df.iterrows():
        movie_id = row["movie_id"]
        title = row["movie_title"]
        year = row["title_year"]
        imdb_id=row["movie_imdb_id"]

        url = IMDB_PLOT_URL.format(imdb_id)
        print(f"[INFO] Scraping {imdb_id} of {title}")

        html = fetch_html(url)
        if not html:
            continue

        synopsis, summaries = parse_plot_page(html)

        rows.append({
            "movie_id": movie_id,
            "imdb_id": imdb_id,
            "title": title,
            "year": year,
            "synopsis": synopsis,
            "summaries": summaries
        })

        time.sleep(random.uniform(*SLEEP_RANGE))

    if not rows:
        print("[WARN] No data scraped")
        return

    out_path = Path(OUTPUT_CSV)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(rows).to_csv(out_path, index=False)
    print(f"[DONE] Saved {len(rows)} movies → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
