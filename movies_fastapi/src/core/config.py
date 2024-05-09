import pathlib

from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent  # abs path to \src
ENV_PATH = pathlib.Path(BASE_DIR, '.env')


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    app_title: str = "Movies"
    # project_name: str = 'movies_fastapi'
    project_host: str = ...
    project_port: int = ...

    prefix: str = '/api/v1'
    docs_url: str = '/api/openapi'
    openapi_url: str = '/api/openapi.json'

    tag_service: str = 'Service'
    tag_films: str = 'Films'
    tag_genres: str = 'Genres'
    tag_persons: str = 'Persons'


class ESSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    es_host: str = ...
    es_port: int = ...
    es_protocol: str = 'http'

    #TODO Delete
    # es_index_names: dict[str, str] = {
    #     'movies': 'movies',
    #     'genres': 'genres',
    #     'persons': 'persons',
    # }

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

index_name = es_settings.es_indexes['movies']['index_name']
index_name = es_settings.es_indexes['movies']['search_fields']
print(index_name)
# print(*es_settings.es_index_names['movies'].keys())