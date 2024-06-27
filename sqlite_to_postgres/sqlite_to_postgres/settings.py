import pathlib
from enum import Enum

from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from utils import create_dir_if_not_exists

BASE_DIR = pathlib.Path(__file__).resolve().parent
ENV_PATH = pathlib.Path(BASE_DIR.parent, '.env')


class InsertToPGMethod(str, Enum):
    INSERT = 'INSERT'
    COPY = 'COPY'


class AppPostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    scheme: str = 'postgresql'
    postgres_user: str = ...
    postgres_password: str = ...
    postgres_host: str = ...
    postgres_port: int = ...
    postgres_db: str = ...
    options: str = '-c search_path=content'

    @property
    def pg_dsn(self) -> PostgresDsn:
        return {
            'dbname': self.postgres_db,
            'user': self.postgres_user,
            'password': self.postgres_password,
            'host': self.postgres_host,
            'port': self.postgres_port,
            'options': self.options
        }


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')
    sqlite_db_path: pathlib.Path = pathlib.Path(BASE_DIR, 'db.sqlite')
    sqlite_ru_db_path: pathlib.Path = pathlib.Path(BASE_DIR, 'ru_db.sqlite')
    csv_tables_path: pathlib.Path = Field('csv_tables',
                                          default_factory=create_dir_if_not_exists(pathlib.Path('csv_tables')))
    delimiter: str = ';'
    chunk_size: int = 200


app_settings = AppSettings()
app_postgres_settings = AppPostgresSettings()
