import pandas as pd
from .db_save import MetadataStore2

chunks_meta = pd.read_csv("data/processed/documents.csv")

store = MetadataStore2()

store.insert_from_dataframe(chunks_meta)

print("Metadata inserted into Postgres")
