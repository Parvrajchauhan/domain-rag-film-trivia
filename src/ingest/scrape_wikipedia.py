# **Wikipedia** - Plot, production, reception
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" 

INPUT_CSV =DATA_DIR / "movie_catalog/final_catalog.csv"
OUTPUT_CSV = DATA_DIR /"raw/wiki_scrap.csv"
MISSING_CSV = DATA_DIR / "raw/wiki_missing.csv"

WIKI_SEARCH_URL = "https://en.wikipedia.org/wiki/{}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

SLEEP_RANGE = (1.2, 2.5)
TIMEOUT = 10


import re
from urllib.parse import quote

def make_wiki_slug(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r"[^\w\s-]", "", title)  
    title = re.sub(r"\s+", " ", title)      
    return title.replace(" ", "_").title()


def build_wiki_url_with_year(title: str, year: int) -> str:
    slug = make_wiki_slug(title)
    return WIKI_SEARCH_URL.format(
        quote(f"{slug}_({year}_film)")
    )

def build_wiki_url_no_year(title: str) -> str:
    slug = make_wiki_slug(title)
    return WIKI_SEARCH_URL.format(
        quote(slug)
    )


def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        return r.text
    except Exception:
        return None

def extract_section(soup, section_id: str) -> str | None:
    h2 = soup.find("h2", {"id": section_id})
    if not h2:
        return None

    heading_div = h2.find_parent("div")
    if not heading_div:
        return None

    content = []

    for sib in heading_div.find_next_siblings():
        if sib.name == "div" and sib.find(["h2"]) is not None:
            break

        if sib.name == "p":
            text = sib.get_text(" ", strip=True)
            if len(text):
                content.append(text)

    return "\n".join(content) if content else None



def main():
    df = pd.read_csv(INPUT_CSV)

    required = {"movie_id", "movie_title","title_year"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required}")

    rows = []
    missing = []

    for _, row in df.iterrows():
        movie_id = row["movie_id"]
        title = row["movie_title"]
        year = row["title_year"]

        wiki_url1 = build_wiki_url_no_year(title)
        wiki_url2 = build_wiki_url_with_year(title, year)

        print(f"[INFO] {title} ({year})")

        html = fetch_html(wiki_url1)

        if not html:
            html = fetch_html(wiki_url2)
            wiki_url = wiki_url2
        else:
            wiki_url = wiki_url1
        if not html:
            missing.append({
                "movie_id": movie_id,
                "title": title,
                "year": year,
                "reason": "page_not_found"
                    })
            print("missing")
            continue
        
        soup = BeautifulSoup(html, "html.parser")
        
        if soup.find("table", {"id": "disambigbox"}):
            missing.append({
                "movie_id": movie_id,
                "title": title,
                "year": year,
                "reason": "disambiguation"
            })
            print("missing")
            continue

        plot = extract_section(soup, "Plot")
        production = extract_section(soup, "Production")
        reception = extract_section(soup, "Reception")

        rows.append({
            "movie_id": movie_id,
            "wiki_url": wiki_url,
            "plot": plot,
            "production": production,
            "reception": reception
        })
        print("found")
        time.sleep(random.uniform(*SLEEP_RANGE))

    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)
    pd.DataFrame(missing).to_csv(MISSING_CSV, index=False)

    print(f"[DONE] Wiki scraped: {len(rows)}")
    print(f"[DONE] Missing pages: {len(missing)} → {MISSING_CSV}")


if __name__ == "__main__":
    main()
