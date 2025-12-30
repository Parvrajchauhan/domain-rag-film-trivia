import pandas as pd
from .metadata_store import MetadataStore

chunks_meta = pd.read_parquet("data/embeddings/chunks_meta.parquet")

store = MetadataStore()

store.insert_from_dataframe(chunks_meta)

print("Metadata inserted into Postgres")
