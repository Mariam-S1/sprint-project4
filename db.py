"""
SQLite client with safe execution helpers.
"""
from typing import Any, List, Tuple
import sqlite3
import pandas as pd

class SQLiteClient:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def run(self, sql: str, params: Tuple[Any, ...] | None = None) -> pd.DataFrame:
        params = params or tuple()
        with self._connect() as conn:
            df = pd.read_sql_query(sql, conn, params=params)
        return df

    def list_tables(self) -> List[str]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            return [r[0] for r in cur.fetchall()]

    def get_table_info(self, table: str) -> pd.DataFrame:
        with self._connect() as conn:
            return pd.read_sql_query(f"PRAGMA table_info({table});", conn)
