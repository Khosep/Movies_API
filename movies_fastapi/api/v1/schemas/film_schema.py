import inspect
from uuid import UUID

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, model_validator, field_validator, validate_call, ValidationError
from typing_extensions import Self

from api.v1.schemas.genre_schema import GenreBase
from api.v1.schemas.person_schema import PersonBase


class FilmBase(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None


class FilmDetails(FilmBase):
    description: str | None
    genres: list[GenreBase]
    actors: list[PersonBase]
    writers: list[PersonBase]
    directors: list[PersonBase]


class FilmQueryExact(BaseModel):
    uuid: UUID | None = None
    title: str | None = None
    imdb_rating: float | None = None

    @model_validator(mode='after')
    def verify_not_empty_dict(self) -> Self:
        if not any([self.uuid, self.title, self.imdb_rating]):
            raise ValueError('At least one field should be provided')
        return self

    @field_validator('imdb_rating')
    @classmethod
    def verify_rating_range(cls, value: float | None) -> float:
        if value is not None:
            if not 1 <= value <= 10:
                raise ValueError('imdb_rating must be between 1 and 10')
            decimal_count = len(str(value).split('.')[1]) if '.' in str(value) else 0
            if decimal_count > 1:
                raise ValueError('imdb_rating must have at most 1 decimal place')
        return value
