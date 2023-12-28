import pathlib

from pydantic import BaseModel, PostgresDsn, DirectoryPath, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent  # abs path to \src
ENV_PATH = pathlib.Path(BASE_DIR, '.env')


#TODO Remove
class PaginationParams(BaseModel):
    limit: int = 10
    offset: int = 0


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

    # es_index_name: str = 'movies'
    # es_index_schema: pathlib.Path = pathlib.Path(BASE_DIR, 'es_index.json')

    @property
    def es_url(self) -> str:
        return f'{self.es_protocol}://{self.es_host}:{self.es_port}'


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding='utf-8', extra='ignore')

    redis_host: str = ...
    redis_port: int = ...


app_settings = AppSettings()
es_settings = ESSettings()
redis_settings = RedisSettings()
