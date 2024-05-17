from uuid import UUID

from pydantic import BaseModel, model_validator
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
    uuid: UUID = None
    title: str = None
    imdb_rating: float = None

    @model_validator(mode='after')
    def verify_not_empty_dict(self) -> Self:
        if not any([self.uuid, self.title, self.imdb_rating]):
            raise ValueError('At least one field should be provided')
        return self
