import os
import re
import glob
import html
import pandas as pd
from bs4 import BeautifulSoup
from unicodedata import normalize
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
OUT_DIR = DATA_DIR / "inbetween"

os.makedirs(OUT_DIR, exist_ok=True)

def strip_html(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ")


def normalize_quotes(text: str) -> str:
    replacements = {
        "“": '"', "”": '"',
        "‘": "'", "’": "'",
        "´": "'",
        "–": "-", "—": "-"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def strip_boilerplate(text: str) -> str:
    boilerplate_patterns = [
        r"\bsee more\b.*$",
        r"\blearn more\b.*$",
        r"edit this page",
        r"contribute to this page",
        r"was this helpful\?",
        r"share this trivia",
        r"spoilers ahead",
    ]

    for pat in boilerplate_patterns:
        text = re.sub(pat, "", text, flags=re.IGNORECASE)

    return text


def normalize_whitespace(text: str) -> str:
    text = normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_text(text: str) -> str:
    text = strip_html(text)
    text = normalize_quotes(text)
    text = strip_boilerplate(text)
    text = normalize_whitespace(text)
    return text


def text_for_hashing(text: str) -> str:
    return clean_text(text).lower()


def process_file(path: str):
    df = pd.read_csv(path, encoding="utf-8")

    TEXT_COLUMNS = {
        "synopsis",
        "summaries",
        "trivia",
        "goofs_continuity",
        "goofs_factual",
        "lead_section",
        "plot_setup",
        "plot_build_up",
        "plot_ending",
        "production",
        "reception",
    }

    present_text_cols = [c for c in TEXT_COLUMNS if c in df.columns]

    out_name = os.path.basename(path).replace(".csv", "_clean.csv")
    out_path = os.path.join(OUT_DIR, out_name)

    if not present_text_cols:
        df.to_csv(out_path, index=False)
        print(f" No text fields found, copied as-is → {out_path}")
        return

    for col in present_text_cols:
        df[f"clean_{col}"] = df[col].apply(clean_text)
        df[f"hash_{col}"] = df[f"clean_{col}"].apply(lambda x: hash(x) if x else None)

    df.to_csv(out_path, index=False)
    print(f" Cleaned columns {present_text_cols} → {out_path}")



def main():
    files = glob.glob(os.path.join(RAW_DIR, "*.csv"))

    if not files:
        raise RuntimeError("No CSV files found in data/raw/")

    for f in files:
        process_file(f)


if __name__ == "__main__":
    main()
