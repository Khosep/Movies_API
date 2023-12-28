from psycopg2.extensions import connection as _connection

from db_dataclasses import map_tables_sqlite_pg
from logger import logger
from pg_loader import PostgresSaver
from settings import app_postgres_settings
from utils import conn_context_psycopg


def clear_data(pg_connection: _connection):
    """Очистить таблицы (postgres)"""

    pg_saver = PostgresSaver(pg_connection)
    pg_saver.clear_tables(map_tables_sqlite_pg)
    logger.debug(f'Database has been cleared')


if __name__ == '__main__':
    with conn_context_psycopg(app_postgres_settings.pg_dsn) as pg_conn:
        clear_data(pg_conn)
