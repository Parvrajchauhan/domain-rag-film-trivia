from sqlalchemy import text
from src.db.session import get_engine
import pandas as pd
from typing import List

#doc_id,text,start_char,end_char,source,section,title

class MetadataStore2:

    def __init__(self):
        self.engine = get_engine()
        self._init_table()

    def _init_table(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS meta (
                    doc_id TEXT PRIMARY KEY,
                    title TEXT,
                    source TEXT,
                    section TEXT,
                    start_char INTEGER,
                    end_char INTEGER,
                    text TEXT NOT NULL
                );
            """))

    def insert_from_dataframe(self, df: pd.DataFrame) -> None:

        required_cols = {
            "doc_id",
            "title",
            "source",
            "section",
            "start_char",
            "end_char",
            "text",
        }

        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        records = [
            {
                "doc_id": row.doc_id,
                "title": row.title,
                "source": row.source,
                "section":row.section,
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
                    INSERT INTO meta (
                        doc_id,
                        title,
                        source,
                        section,
                        start_char,
                        end_char,
                        text
                    )
                    VALUES (
                        :doc_id,
                        :title,
                        :source,
                        :section,
                        :start_char,
                        :end_char,
                        :text
                    )
                    ON CONFLICT (doc_id) DO NOTHING
                """),
                records,
            )

    def fetch_by_doc_ids(self, doc_id: List[int]):
        if not doc_id:
            return []

        with self.engine.begin() as conn:
            result = conn.execute(
                text("""
                    SELECT
                        doc_id,
                        title,
                        source,
                        section,
                        start_char,
                        end_char,
                        text
                    FROM meta
                    WHERE doc_id = ANY(:doc_id)
                    ORDER BY doc_id
                """),
                {"doc_id": doc_id},
            )
            return result.fetchall()
