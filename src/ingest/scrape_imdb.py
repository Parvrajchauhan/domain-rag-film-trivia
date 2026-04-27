# **OMDB API** - Plot, year, director, genre, runtime
# Uses OMDB API instead of scraping IMDB directly (avoids bot detection / 202 errors)

import time
import random
import requests
import pandas as pd
from pathlib import Path

DATA_DIR   = Path(__file__).resolve().parent.parent.parent / "data"
INPUT_CSV  = DATA_DIR / "movie_catalog/final_catalog.csv"
OUTPUT_CSV = DATA_DIR / "raw/imdb_movies.csv"

OMDB_API_KEY  = "fd43f5ac"        
OMDB_BASE_URL = "https://www.omdbapi.com/"

SLEEP_RANGE = (0.5, 1.2)   # OMDB is an API, so shorter delays are fine
TIMEOUT     = 10
MAX_RETRIES = 3


def fetch_omdb(imdb_id: str) -> dict | None:
    params = {
        "i":      imdb_id,
        "apikey": OMDB_API_KEY,
        "plot":   "full",   
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(OMDB_BASE_URL, params=params, timeout=TIMEOUT)

            if r.status_code == 200:
                data = r.json()
                if data.get("Response") == "True":
                    return data
                else:
                    print(f"[WARN] OMDB error for {imdb_id}: {data.get('Error')}")
                    return None

            elif r.status_code == 401:
                print(f"[ERROR] Invalid API key. Get one at https://www.omdbapi.com/apikey.aspx")
                raise SystemExit(1)

            elif r.status_code == 429:
                wait = 60 
                print(f"[WARN] Rate limited (429). Waiting {wait}s...")
                time.sleep(wait)

            else:
                print(f"[WARN] Unexpected status {r.status_code} for {imdb_id} (attempt {attempt})")

        except requests.exceptions.Timeout:
            print(f"[WARN] Timeout for {imdb_id} (attempt {attempt})")
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR] Connection error for {imdb_id}: {e}")
            return None

        if attempt < MAX_RETRIES:
            time.sleep(2 ** attempt) 

    print(f"[FAIL] Gave up on {imdb_id} after {MAX_RETRIES} attempts")
    return None


def parse_omdb(data: dict) -> dict:
    def clean(val):
        return None if val in (None, "N/A", "") else val.strip()

    # Runtime: OMDB returns "142 min" → extract just the integer
    runtime_raw = clean(data.get("Runtime"))
    runtime_min = None
    if runtime_raw:
        parts = runtime_raw.split()
        if parts[0].isdigit():
            runtime_min = int(parts[0])

    # IMDB rating: OMDB returns it as a string "8.4"
    imdb_rating_raw = clean(data.get("imdbRating"))
    imdb_rating = float(imdb_rating_raw) if imdb_rating_raw else None

    return {
        "synopsis":    clean(data.get("Plot")),
        "year":        clean(data.get("Year")),
        "director":    clean(data.get("Director")),
        "genre":       clean(data.get("Genre")),
        "runtime_min": runtime_min,
        "language":    clean(data.get("Language")),
        "country":     clean(data.get("Country")),
        "imdb_rating": imdb_rating,
        "awards":      clean(data.get("Awards")),
        "actors":      clean(data.get("Actors")),
    }


def main():
    df = pd.read_csv(INPUT_CSV)

    required_cols = {"movie_id", "movie_title", "title_year", "movie_imdb_id"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")

    rows = []
    total = len(df)

    for i, row in df.iterrows():
        movie_id = row["movie_id"]
        title    = row["movie_title"]
        imdb_id  = row["movie_imdb_id"]

        print(f"[INFO] ({i+1}/{total}) Fetching {imdb_id} — {title}")

        data = fetch_omdb(imdb_id)
        if not data:
            # Still append a skeleton row so we know this movie was attempted
            rows.append({
                "movie_id": movie_id,
                "imdb_id":  imdb_id,
                "title":    title,
                **{k: None for k in ["synopsis", "year", "director", "genre",
                                     "runtime_min", "language", "country",
                                     "imdb_rating", "awards", "actors"]},
            })
            continue

        parsed = parse_omdb(data)
        rows.append({
            "movie_id": movie_id,
            "imdb_id":  imdb_id,
            "title":    title,
            **parsed,
        })

        time.sleep(random.uniform(*SLEEP_RANGE))

    if not rows:
        print("[WARN] No data scraped")
        return

    out_path = Path(OUTPUT_CSV)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    result_df = pd.DataFrame(rows)
    result_df.to_csv(out_path, index=False)

    success = result_df["synopsis"].notna().sum()
    print(f"[DONE] {success}/{len(rows)} movies fetched successfully → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()