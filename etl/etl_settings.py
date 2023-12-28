import enum
import pathlib

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = pathlib.Path(__file__).resolve().parent
ENV_PATH = pathlib.Path(BASE_DIR.parent, '.env')

class Index(enum.Enum):
    MOVIES = 0
    GENRES = 1
    PERSONS = 2

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


class ESSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    es_host: str = ...
    es_port: int = ...
    es_protocol: str = 'http'
    es_indexes_names: list[str] = ['movies', 'genres', 'persons']

    # es_index_schema: pathlib.Path = pathlib.Path(BASE_DIR, 'es_indexes', 'films_es_index.json')
    es_indexes_dir: pathlib.Path = pathlib.Path(BASE_DIR, 'es_indexes')

    @property
    def es_url(self) -> str:
        return f'{self.es_protocol}://{self.es_host}:{self.es_port}'

    @property
    def es_indexes(self) -> dict[str, str]:
        return {
            self.es_indexes_names[0]: 'movies_es_index.json',
            self.es_indexes_names[1]: 'genres_es_index.json',
            self.es_indexes_names[2]: 'persons_es_index.json',
        }

    @property
    def sql_files(self) -> dict[str, str]:
        return {
            self.es_indexes_names[0]: 'movies_query.sql',
            self.es_indexes_names[1]: 'genres_query.sql',
            self.es_indexes_names[2]: 'persons_query.sql',
        }


class ETLSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    chunk_size: int = 111
    state_key: str = 'latest_updated_at'
    sql_dir: pathlib.Path = pathlib.Path(BASE_DIR, 'sql')


app_postgres_settings = AppPostgresSettings()
es_settings = ESSettings()
etl_settings = ETLSettings()
