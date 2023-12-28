import json
import pathlib
from datetime import datetime
from functools import wraps
from logging import Logger
from typing import Generator

import psycopg

from etl_settings import es_settings
from state.state import State


def coroutine(func):
    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        next(fn)
        return fn

    return inner


def get_json_data(file_path: pathlib.Path) -> dict:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def create_sql_trigger_if_not_exists(file_path: pathlib.Path,
                                     trigger_name: str,
                                     conn: psycopg.Connection,
                                     pg_cursor: psycopg.ServerCursor,
                                     logger: Logger
                                     ):
    """Create trigger (in datatbase) for tracking changes to the table (UPDATE or INSERT)."""
    # Check if the trigger  exists
    pg_cursor.execute(f"SELECT 1 FROM pg_trigger WHERE tgname = '{trigger_name}'")
    trigger_exists = bool(pg_cursor.fetchone())

    if not trigger_exists:
        with open(file_path, 'r') as file:
            trigger_sql = file.read()
        conn.execute(trigger_sql)
        conn.commit()
        logger.info(f'Trigger {trigger_name} created')


def create_sql_func_if_not_exists(file_path: pathlib.Path,
                                  func_name: str,
                                  conn: psycopg.Connection,
                                  pg_cursor: psycopg.ServerCursor,
                                  logger: Logger
                                  ):
    """Create function (in database) to notify etl process about triggered event."""
    # Check if the function  exists
    pg_cursor.execute(f"SELECT 1 FROM pg_proc WHERE proname = '{func_name}'")
    function_exists = bool(pg_cursor.fetchone())
    logger.info(f'{func_name}: {function_exists}')

    if not function_exists:
        with open(file_path, 'r') as file:
            func_sql = file.read()
        conn.execute(func_sql)
        conn.commit()
        logger.info(f'Function {func_name} created')


def start_etl_process(extractor_coro: Generator, state: State, logger: Logger):
    for index_name in es_settings.es_indexes_names:
        last_updated = state.get_state(f'{index_name}_last_updated') or str(datetime.min)
        logger.debug(f'ETL process has started for {index_name} ({last_updated})')
        extractor_coro.send((last_updated, index_name))
