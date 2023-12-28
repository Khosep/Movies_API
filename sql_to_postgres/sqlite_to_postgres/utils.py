import sqlite3
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor


@contextmanager
def conn_context_sqlite(db_path: Path):
    try:
        sqlite_conn = sqlite3.connect(db_path)
        # sqlite3.Row highly optimized row_factory for Connection objects,
        # It supports iteration, equality testing, len(), and mapping access by column name and index.
        # https://docs.python.org/3/library/sqlite3.html#sqlite3.Row
        sqlite_conn.row_factory = sqlite3.Row
        yield sqlite_conn
    finally:
        sqlite_conn.close()


@contextmanager
def conn_context_psycopg(pg_dsn: dict):
    try:
        pg_conn = psycopg2.connect(**pg_dsn, cursor_factory=RealDictCursor)
        yield pg_conn
    finally:
        pg_conn.close()


def create_dir_if_not_exists(directory_path: Path):
    directory_path.mkdir(parents=True, exist_ok=True)
