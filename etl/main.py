import enum
import pathlib
import time
from datetime import datetime
from logging import Logger

import psycopg
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row

from es_loader import ElasticsearhClient, ElasticsearchLoader
from etl_settings import app_postgres_settings, etl_settings, es_settings
from etl_utils import create_sql_func_if_not_exists, create_sql_trigger_if_not_exists, start_etl_process
from logger import logger
from pg_extractor import PostgresExtractor
from pg_to_es_transformer import PostgresToElasticsearchTransformer
from state.json_file_storage import JsonFileStorage
from state.state import State

TIME_SLEEP = 22.2
FUNC_NOTIFY_FILE = pathlib.Path(etl_settings.sql_dir, 'func_notify.sql')
TRIGGER_FILE = pathlib.Path(etl_settings.sql_dir, 'trigger.sql')


class WaitingType(enum.Enum):
    TRIGGER = 0
    SLEEP = 1


def etl_process(conn: psycopg.Connection,
                pg_cursor: psycopg.ServerCursor,
                waiting_type: int,
                logger: Logger) -> None:
    state = State(JsonFileStorage(logger))

    es_client = ElasticsearhClient()

    for index_name in es_settings.es_indexes_names:
        index_path = es_settings.es_indexes_dir / es_settings.es_indexes[index_name]
        es_client.create_index_if_not_exists(index_name, index_path)

    # Create etl instances
    pg_extractor = PostgresExtractor(pg_cursor, logger)
    pg_to_es_transformer = PostgresToElasticsearchTransformer(logger)
    es_loader = ElasticsearchLoader(logger)

    loader_coro = es_loader.load(state)
    transformer_coro = pg_to_es_transformer.transform(next_node=loader_coro)
    extractor_coro = pg_extractor.extract(next_node=transformer_coro)

    # Waiting for db trigger
    if waiting_type == WaitingType.TRIGGER.value:
        # Create trigger set: func + trigger
        create_sql_func_if_not_exists(FUNC_NOTIFY_FILE, 'notify_etl', conn,
                                      pg_cursor, logger)
        create_sql_trigger_if_not_exists(TRIGGER_FILE, 'update_insert_trigger', conn,
                                         pg_cursor, logger)

        # Create channel for listening
        channel = psycopg.connect(pg_dsn, autocommit=True)
        channel.execute('LISTEN update_or_insert_event')

        notify_gen = channel.notifies()
        logger.info('Listening...')
        for notify in notify_gen:
            logger.info(f'{notify=}')

            start_etl_process(extractor_coro, state, logger)
            logger.info('ETL process is completed')

    # Make periodic queries to the database
    else:
        while True:
            start_etl_process(extractor_coro, state, logger)
            logger.info(f'ETL process is completed. Sleeping {TIME_SLEEP}s')
            time.sleep(TIME_SLEEP)


if __name__ == '__main__':
    pg_dsn = make_conninfo(**app_postgres_settings.pg_dsn)

    with (psycopg.connect(pg_dsn, row_factory=dict_row) as conn,
          psycopg.ServerCursor(conn, 'fetcher') as pg_cursor):
        waiting_type = WaitingType.SLEEP.value
        etl_process(conn, pg_cursor, waiting_type, logger)
