from pydantic import Field, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict()

    PROJECT_NAME: str = Field(default="test_movies")

    REDIS_HOST: str = Field(default="127.0.0.1")
    REDIS_PORT: int = Field(default=6379)

    ES_HOST: str = Field(default="127.0.0.1")
    ES_PORT: int = Field(default=9200)

    FASTAPI_HOST: str = Field(default="127.0.0.1")
    FASTAPI_PORT: int = Field(default=8000)

    @property
    def app_url(self) -> HttpUrl:
        return f"http://{self.FASTAPI_HOST}:{self.FASTAPI_PORT}"

    @property
    def es_url(self) -> HttpUrl:
        return f"http://{self.ES_HOST}:{self.ES_PORT}"

    @property
    def redis_dsn(self) -> RedisDsn:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


test_settings = TestSettings()
index_settings = IndexSettings()
