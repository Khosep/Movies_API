from enum import Enum
from typing import Any

from pydantic import Field, HttpUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class IndexName(str, Enum):
    GENRES = "genres"
    MOVIES = "movies"
    PERSONS = "persons"

    def __str__(self) -> str:
        return str.__str__(self)


class IndexSettings(BaseSettings):
    model_config = SettingsConfigDict(use_enum_values=True)

    settings: dict[str, Any] = {
        "refresh_interval": "1s",
        "analysis": {
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"},
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english",
                },
                "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                "russian_stemmer": {"type": "stemmer", "language": "russian"},
            },
            "analyzer": {
                "ru_en": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                        "english_possessive_stemmer",
                        "russian_stop",
                        "russian_stemmer",
                    ],
                }
            },
        },
    }
    mappings: dict[IndexName, Any] = {
        IndexName.GENRES: {
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword"
                },
                "name": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                }
            }
        },
        IndexName.MOVIES: {
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword"
                },
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                },
                "imdb_rating": {
                    "type": "float"
                },
                "description": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "genres": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "actors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "writers": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "directors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "full_name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                }
            }
        },
        IndexName.PERSONS: {
            "dynamic": "strict",
            "properties": {
                "uuid": {
                    "type": "keyword"
                },
                "full_name": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                },
                "films": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "uuid": {
                            "type": "keyword"
                        },
                        "title": {
                            "type": "keyword"
                        },
                        "imdb_rating": {
                            "type": "float"
                        },
                        "roles": {
                            "type": "keyword"
                        }
                    }
                }
            }
        }
    }


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict()

    project_name: str = Field(default="test_movies")
    prefix: str = '/api/v1'

    redis_host: str = Field(default="127.0.0.1")
    redis_port: int = Field(default=6379)

    es_host: str = Field(default="127.0.0.1")
    es_port: int = Field(default=9200)

    fastapi_host: str = Field(default="127.0.0.1")
    fastapi_port: int = Field(default=8000)

    @property
    def app_url(self) -> HttpUrl:
        return f"http://{self.fastapi_host}:{self.fastapi_port}"

    @property
    def es_url(self) -> HttpUrl:
        return f"http://{self.es_host}:{self.es_port}"

    @property
    def redis_dsn(self) -> RedisDsn:
        return f"redis://{self.redis_host}:{self.redis_port}"


test_settings = TestSettings()
index_settings = IndexSettings()
