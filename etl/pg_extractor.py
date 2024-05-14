import pathlib
from logging import Logger
from typing import Generator, Any

from etl_settings import etl_settings, es_settings
from etl_utils import coroutine

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent


class PostgresExtractor:
    """Class for extracting data from Postgres."""

    def __init__(self, cursor, logger: Logger):
        self.cur = cursor
        self.chunk_size = etl_settings.chunk_size
        self._logger = logger

    @coroutine
    def extract(self, next_node: Generator) -> Generator[dict[str, Any], tuple[str, str], None]:
        while data := (yield):
            last_updated, index_name = data
            self._logger.info(f'Check if there are any data later than {last_updated}')
            sql_query = self._get_sql_query(index_name)
            self.cur.execute(sql_query, (last_updated,))

            while results := self.cur.fetchmany(size=self.chunk_size):
                total_data = dict(index_name=index_name, data=results)
                self._logger.info(f'Extracted list of data with len={len(results)} sent for "{index_name}"')
                next_node.send(total_data)

    def _get_sql_query(self, index_name: str) -> str:
        sql_file = pathlib.Path(etl_settings.sql_dir, es_settings.sql_files[index_name])
        with open(sql_file, 'r') as file:
            sql_query = file.read()
            self._logger.info(f'get sql_query for "{index_name}"')
            self._logger.debug(f'{sql_query=}')
        return sql_query
