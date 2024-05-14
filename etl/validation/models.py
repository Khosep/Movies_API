import enum
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class RoleEnum(enum.Enum):
    actor = 'actor'
    writer = 'writer'
    director = 'director'


class PGMoviePerson(BaseModel):
    """Person used for PGMovie"""
    id: uuid.UUID
    full_name: str


class PGMovieGenre(BaseModel):
    """Genre used for PGMovie"""
    id: uuid.UUID
    name: str


class PGMovie(BaseModel):
    """Get from movies_query.sql"""
    id: uuid.UUID
    title: str
    rating: float | None
    description: str | None
    updated_at: datetime
    genres: list[PGMovieGenre]
    actors: list[PGMoviePerson]
    writers: list[PGMoviePerson]
    directors: list[PGMoviePerson]


class PGGenre(BaseModel):
    """Get from genres_query.sql"""
    id: uuid.UUID
    name: str
    updated_at: datetime


class PGPersonFilms(BaseModel):
    """Films used for PGPerson"""
    model_config = ConfigDict(use_enum_values=True)
    film_work_id: uuid.UUID
    title: str
    rating: float | None
    roles: list[RoleEnum]


class PGPerson(BaseModel):
    """Get from persons_query.sql"""
    id: uuid.UUID
    full_name: str
    updated_at: datetime
    films: list[PGPersonFilms]


class ESMovieGenre(BaseModel):
    uuid: uuid.UUID
    name: str


class ESMoviePerson(BaseModel):
    uuid: uuid.UUID
    full_name: str


class ESMovie(BaseModel):
    """Use for index 'movies'"""
    uuid: uuid.UUID
    title: str
    imdb_rating: float | None
    description: str | None
    genres: list[ESMovieGenre] = Field(default_factory=list)
    actors: list[ESMoviePerson] = Field(default_factory=list)
    writers: list[ESMoviePerson] = Field(default_factory=list)
    directors: list[ESMoviePerson] = Field(default_factory=list)


class ESGenre(BaseModel):
    """Use for index 'genres'"""
    uuid: uuid.UUID
    name: str


class ESPersonFilms(BaseModel):
    """Films used for ESPerson"""
    model_config = ConfigDict(use_enum_values=True)
    title: str
    imdb_rating: float | None
    uuid: uuid.UUID
    roles: list[RoleEnum]


class ESPerson(BaseModel):
    """Use for index 'persons'"""
    uuid: uuid.UUID
    full_name: str
    films: list[ESPersonFilms]
