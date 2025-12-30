from sqlalchemy import text
from src.db.session import get_engine
import pandas as pd
from typing import List


class MetadataStore:
    """
    Metadata store aligned with FAISS implicit vector IDs.
    Uses SQLAlchemy engine + raw SQL (predictable & fast).
    """

    def __init__(self):
        self.engine = get_engine()
        self._init_table()

    def _init_table(self) -> None:
        """
        Create metadata table if it does not exist.
        """
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chunks (
                    vector_id INTEGER PRIMARY KEY,
                    chunk_id TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    title TEXT,
                    source TEXT,
                    start_char INTEGER,
                    end_char INTEGER,
                    text TEXT NOT NULL
                );
            """))

    def insert_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Insert metadata rows from DataFrame.

        EXPECTS:
        - DataFrame contains explicit `vector_id`
        - vector_id matches FAISS implicit IDs exactly
        """

        required_cols = {
            "vector_id",
            "chunk_id",
            "doc_id",
            "title",
            "source",
            "start_char",
            "end_char",
            "text",
        }

        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        records = [
            {
                "vector_id": row.vector_id,
                "chunk_id": row.chunk_id,
                "doc_id": row.doc_id,
                "title": row.title,
                "source": row.source,
                "start_char": row.start_char,
                "end_char": row.end_char,
                "text": row.text,
            }
            for row in df.itertuples(index=False)
        ]

        if not records:
            return

        with self.engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO chunks (
                        vector_id,
                        chunk_id,
                        doc_id,
                        title,
                        source,
                        start_char,
                        end_char,
                        text
                    )
                    VALUES (
                        :vector_id,
                        :chunk_id,
                        :doc_id,
                        :title,
                        :source,
                        :start_char,
                        :end_char,
                        :text
                    )
                    ON CONFLICT (vector_id) DO NOTHING
                """),
                records,
            )

    def fetch_by_vector_ids(self, vector_ids: List[int]):
        """
        Fetch metadata rows by FAISS vector IDs.
        """
        if not vector_ids:
            return []

        with self.engine.begin() as conn:
            result = conn.execute(
                text("""
                    SELECT
                        vector_id,
                        chunk_id,
                        doc_id,
                        title,
                        source,
                        start_char,
                        end_char,
                        text
                    FROM chunks
                    WHERE vector_id = ANY(:vector_ids)
                    ORDER BY vector_id
                """),
                {"vector_ids": vector_ids},
            )
            return result.fetchall()
