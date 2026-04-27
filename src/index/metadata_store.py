from sqlalchemy import text
from src.db.session import get_engine
import pandas as pd
from typing import List


class MetadataStore:

    def __init__(self):
        self.engine = get_engine()
        self._init_table()

    def _init_table(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chunks (
                    vector_id SERIAL PRIMARY KEY,

                    chunk_id TEXT NOT NULL,
                    doc_id TEXT NOT NULL,

                    text TEXT NOT NULL,

                    source TEXT,
                    section TEXT,
                    title TEXT
                );
            """))

    def insert_from_dataframe(self, df: pd.DataFrame) -> None:

        required_cols = {
            "chunk_id",
            "doc_id",
            "text"
        }

        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        records = [
            {
                "chunk_id": row.chunk_id,
                "doc_id": row.doc_id,
                "text": row.text,
                "source": getattr(row, "source", None),
                "section": getattr(row, "section", None),
                "title": getattr(row, "title", None),
            }
            for row in df.itertuples(index=False)
        ]

        if not records:
            return

        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO chunks (
                        chunk_id,
                        doc_id,
                        text,
                        source,
                        section,
                        title
                    )
                    VALUES (
                        :chunk_id,
                        :doc_id,
                        :text,
                        :source,
                        :section,
                        :title
                    )
                    ON CONFLICT DO NOTHING
                """),
                records,
            )

    def fetch_by_vector_ids(self, vector_ids: List[int]):
        if not vector_ids:
            return []

        with self.engine.begin() as conn:
            result = conn.execute(
                text("""
                    SELECT
                        vector_id,
                        chunk_id,
                        doc_id,
                        text,
                        source,
                        section,
                        title
                    FROM chunks
                    WHERE vector_id = ANY(:vector_ids)
                    ORDER BY vector_id
                """),
                {"vector_ids": vector_ids},
            )
            return result.fetchall()