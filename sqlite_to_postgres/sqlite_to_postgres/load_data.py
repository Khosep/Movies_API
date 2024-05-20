import sqlite3
import time

from db_dataclasses import map_tables_sqlite_pg
from logger import logger
from pg_loader import PostgresSaver
from psycopg2.extensions import connection as _connection
from settings import app_settings, app_postgres_settings, InsertToPGMethod
from sqlite_extractor import SQLiteExtractor
from utils import conn_context_sqlite, conn_context_psycopg

INSERT_METHOD = InsertToPGMethod.COPY.value


def load_from_sqlite(connection: sqlite3.Connection, pg_connection: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    sqlite_extractor = SQLiteExtractor(connection)
    pg_saver = PostgresSaver(pg_connection)

    pg_saver.clear_tables(map_tables_sqlite_pg)

    start = time.perf_counter()
    if INSERT_METHOD == 'INSERT':
        # Option 1: INSERT
        for table_name in map_tables_sqlite_pg:
            for rows in sqlite_extractor.extract_data(table_name):
                pg_saver.load_by_multi_insert(table_name, rows)
    else:
        # Option 2: COPY
        sqlite_extractor.save_table_to_file()
        for table_name in map_tables_sqlite_pg:
            pg_saver.load_by_copy(table_name)
    end = time.perf_counter()

    logger.warning(f'Time for "{INSERT_METHOD}": {round(end - start, 2)}s')


if __name__ == '__main__':
    with conn_context_sqlite(app_settings.sqlite_db_path) as sqlite_conn:
        with conn_context_psycopg(app_postgres_settings.pg_dsn) as pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
