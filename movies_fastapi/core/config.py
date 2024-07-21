import pathlib

from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent  # abs path to /movies_fastapi
ENV_PATH = pathlib.Path(BASE_DIR.parent, '.env')   # path to movies_fastapi/.env


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    app_title: str = 'Movies'
    # project_name: str = 'movies_fastapi'
    project_host: str = 'localhost'
    project_port: int = 8000

    prefix: str = '/api/v1'
    docs_url: str = '/api/openapi'
    openapi_url: str = '/api/openapi.json'

    tag_service: str = 'Service'
    tag_films: str = 'Films'
    tag_genres: str = 'Genres'
    tag_persons: str = 'Persons'

    page_size: int = 20


class ESSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    es_host: str = ...
    es_port: int = ...
    es_protocol: str = 'http'

    # tuple: (index_name, search_fields)
    es_index_names: dict[str, tuple] = {
        'movies': ('movies', ['title']),
        'genres': ('genres', ['name']),
        'persons': ('persons', ['full_name']),
    }
    es_indexes: dict[str, dict] = {
        'movies': {'index_name': 'movies', 'search_fields': ['title']},
        'genres': {'index_name': 'genres', 'search_fields': ['name']},
        'persons': {'index_name': 'persons', 'search_fields': ['full_name']},
    }

    @property
    def es_url(self) -> str:
        return f'{self.es_protocol}://{self.es_host}:{self.es_port}'


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    redis_host: str = ...
    redis_port: int = ...
    redis_cache_expiration_time_sec: int = 1 * 60

    @property
    def redis_url(self) -> RedisDsn:
        return f'redis://{self.redis_host}:{self.redis_port}'


app_settings = AppSettings()
es_settings = ESSettings()
redis_settings = RedisSettings()