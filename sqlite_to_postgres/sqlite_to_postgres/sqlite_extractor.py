import csv
import pathlib
import sqlite3
from dataclasses import fields
from pathlib import Path

from db_dataclasses import map_tables_sqlite_pg
from logger import logger
from settings import app_settings


class SQLiteExtractor:
    def __init__(self, conn):
        self.conn = conn
        self.table_names = self._get_table_names()

    def _get_table_names(self) -> list[str]:
        cur = self.conn.cursor()
        tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        cur.close()
        table_names = [table[0] for table in tables]
        return table_names

    def save_table_to_file(self) -> None:
        for table in self.table_names:
            cur = self.conn.cursor()
            csv_file_path = Path(app_settings.csv_tables_path, f'{table}.csv')
            target_table = map_tables_sqlite_pg[table]
            column_names = ', '.join([field.name for field in fields(target_table)])
            sql_stmt = f'SELECT {column_names} FROM {table};'
            cur.execute(sql_stmt)
            self._write_to_csv(cur, csv_file_path)
            cur.close()

    @staticmethod
    def _write_to_csv(cur: sqlite3.Cursor, csv_file_path: pathlib.Path) -> None:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=app_settings.delimiter)
            writer.writerow([i[0] for i in cur.description])
            writer.writerows(cur)
            logger.info(f'{csv_file_path} is recorded)')

    def extract_data(self, table_name):
        model = map_tables_sqlite_pg[table_name]
        cur = self.conn.cursor()
        cur.row_factory = sqlite3.Row
        column_names = ", ".join(field.name for field in fields(model))
        sql_stmt = f'SELECT {column_names} FROM {table_name};'
        cur.execute(sql_stmt)
        while rows := cur.fetchmany(app_settings.chunk_size):
            yield [model(**dict(row)) for row in rows]
