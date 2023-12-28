from dataclasses import fields, astuple
from pathlib import Path

from psycopg2 import sql

from db_dataclasses import map_tables_sqlite_pg
from logger import logger
from settings import app_settings


class PostgresSaver:
    def __init__(self, conn):
        self.conn = conn

    def load_by_multi_insert(self, table_name: str, rows):
        """Use INSERT (multiple rows) statement."""
        model = map_tables_sqlite_pg[table_name]
        with self.conn.cursor() as cur:
            column_names = ", ".join(field.name for field in fields(model))
            placeholder = ", ".join(["%s"] * len(fields(model)))
            values = ','.join(cur.mogrify(f'({placeholder})', astuple(row)).decode('utf-8') for row in rows)
            sql_stmt = f'INSERT INTO {table_name} ({column_names}) VALUES {values} ON CONFLICT (id) DO NOTHING;'
            cur.execute(sql_stmt)
            # Здесь и далее: применяем conn.commit(), поскольку используем автоматическое закрытие соединение с БД через
            # @contextmanager (from contextlib) (либо если бы использовали closing (from contextlib)).
            # Если бы применяли просто with psycopg2.connect (без посредника для автозакрытия соединения),
            # то согласно документации блок 'with conn.cursor() ...' сам бы сделал commit.
            self.conn.commit()
            logger.info(f'data for {table_name} is loaded by INSERT')

    def load_by_copy(self, table_name) -> None:
        """Use COPY statement."""
        with self.conn.cursor() as cur:
            file_path = Path(app_settings.csv_tables_path, f'{table_name}.csv')
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_stmt = sql.SQL("COPY {table} FROM STDIN DELIMITER ';' CSV HEADER;"
                                   ).format(table=sql.Identifier(table_name))
                cur.copy_expert(sql_stmt, file)
                self.conn.commit()
                logger.info(f'data for {table_name} is loaded by COPY')

    def clear_tables(self, table_names: list[str] | dict) -> None:
        with self.conn.cursor() as cur:
            tables_line = ', '.join(table_names)
            cur.execute(f'TRUNCATE {tables_line} CASCADE')
            self.conn.commit()
            logger.info(f'tables is cleared')
