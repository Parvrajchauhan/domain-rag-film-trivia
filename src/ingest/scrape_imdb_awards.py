# **IMDb** — Awards (event-based) + Box Office (UPDATED DOM)

import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

INPUT_CSV = DATA_DIR / "movie_catalog/final_catalog.csv"
OUTPUT_CSV = DATA_DIR / "raw/imdb_awards_boxoffice.csv"

IMDB_AWARDS_URL = "https://www.imdb.com/title/{}/awards/"
IMDB_MAIN_URL = "https://www.imdb.com/title/{}/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

TIMEOUT = 10
SLEEP_RANGE = (1.5, 3.0)


def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        return r.text
    except Exception:
        return None


def extract_awards_with_headings(html: str) -> tuple[str | None, str | None]:
    soup = BeautifulSoup(html, "html.parser")

    wins = []
    nominations = []

    # Each award block (Academy Awards, ASC, etc.)
    sections = soup.select('div[data-testid^="sub-section-ev"]')

    for section in sections:
        # Find event title ABOVE this section
        title_div = section.find_previous(
            "div", class_="ipc-title--section-title"
        )

        if not title_div:
            continue

        event_name = title_div.get_text(" ", strip=True)

        # Each award entry is a <li>
        items = section.select('li[data-testid="list-item"]')

        for item in items:
            text = item.get_text(" ", strip=True)

            if not text:
                continue

            # Normalize prefixes
            if "Winner" in text:
                wins.append(f"{event_name} — {text}")
            elif "Nominee" in text:
                nominations.append(f"{event_name} — {text}")

    return (
        " || ".join(dict.fromkeys(wins)) if wins else None,
        " || ".join(dict.fromkeys(nominations)) if nominations else None,
    )



# -------- BOX OFFICE --------
def extract_box_office(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    data = {
        "budget": None,
        "opening_weekend_us_canada": None,
        "gross_us_canada": None,
        "gross_worldwide": None,
    }

    section = soup.find("div", {"data-testid": "title-boxoffice-section"})
    if not section:
        return data

    def get_value(testid: str) -> str | None:
        li = section.find("li", {"data-testid": testid})
        if not li:
            return None
        val = li.find("span", class_="ipc-metadata-list-item__list-content-item")
        return val.get_text(strip=True) if val else None

    data["budget"] = get_value("title-boxoffice-budget")
    data["gross_us_canada"] = get_value("title-boxoffice-grossdomestic")
    data["opening_weekend_us_canada"] = get_value(
        "title-boxoffice-openingweekenddomestic"
    )
    data["gross_worldwide"] = get_value(
        "title-boxoffice-cumulativeworldwidegross"
    )

    return data


def main():
    df = pd.read_csv(INPUT_CSV)

    required = {"movie_id", "movie_title", "title_year", "movie_imdb_id"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required}")

    rows = []

    for _, row in df.iterrows():
        movie_id = row["movie_id"]
        title = row["movie_title"]
        year = row["title_year"]
        imdb_id = row["movie_imdb_id"]

        print(f"[INFO] IMDb Awards + Box Office: {title} ({year})")

        awards_html = fetch_html(IMDB_AWARDS_URL.format(imdb_id))
        main_html = fetch_html(IMDB_MAIN_URL.format(imdb_id))

        if not awards_html or not main_html:
            continue

        wins, nominations = extract_awards_with_headings(awards_html)
        box = extract_box_office(main_html)

        rows.append({
            "movie_id": movie_id,
            "imdb_id": imdb_id,
            "title": title,
            "year": year,
            "award_wins": wins,
            "award_nominations": nominations,
            "budget": box["budget"],
            "opening_weekend_us_canada": box["opening_weekend_us_canada"],
            "gross_us_canada": box["gross_us_canada"],
            "gross_worldwide": box["gross_worldwide"],
        })

        time.sleep(random.uniform(*SLEEP_RANGE))

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)

    print(f"[DONE] Saved {len(rows)} movies → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
