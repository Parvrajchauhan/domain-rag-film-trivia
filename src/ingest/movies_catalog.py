import pandas as pd
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "movie_catalog"
df = pd.read_csv(DATA_DIR / "movie_metadata.csv")

df = df.dropna(subset=["movie_title", "title_year", "movie_imdb_link", "num_voted_users"])
df = df.drop_duplicates(subset=["movie_imdb_link"])

df_top = (
    df.sort_values("num_voted_users", ascending=False)
      .head(250)
      .reset_index(drop=True)
)

def extract_imdb_id(url):
    match = re.search(r"(tt\d+)", str(url))
    return match.group(1) if match else None

final_df = pd.DataFrame({
    "movie_id": range(1, len(df_top) + 1),
    "movie_title": df_top["movie_title"].str.strip(),
    "title_year": df_top["title_year"].astype(int),
    "movie_imdb_link": df_top["movie_imdb_link"],
    "movie_imdb_id": df_top["movie_imdb_link"].apply(extract_imdb_id)
})

final_df.to_csv(DATA_DIR /"final_catalog.csv", index=False)

print("final_catalog.csv created successfully")
