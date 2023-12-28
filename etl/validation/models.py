import uuid
import enum
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

class RoleEnum(enum.Enum):
    actor = 'actor'
    writer = 'writer'
    director = 'director'

class PGMoviePerson(BaseModel):
    """Person used for PGMovie"""
    person_id: uuid.UUID
    person_name: str
    person_role: str

class PGMovie(BaseModel):
    """Get from movies_query.sql"""
    id: uuid.UUID
    title: str
    description: str | None
    rating: float | None
    updated_at: datetime
    persons: list[PGMoviePerson]
    genres: list[str]

class PGGenre(BaseModel):
    """Get from genres_query.sql"""
    id: uuid.UUID
    name: str
    updated_at: datetime


class PGPersonFilms(BaseModel):
    """Films used for PGPerson"""
    model_config = ConfigDict(use_enum_values=True)
    film_work_id: uuid.UUID
    roles: list[RoleEnum]


class PGPerson(BaseModel):
    """Get from persons_query.sql"""
    id: uuid.UUID
    full_name: str
    updated_at: datetime
    films: list[PGPersonFilms]


class ESMoviePerson(BaseModel):
    id: uuid.UUID
    name: str

class ESMovie(BaseModel):
    """Use for index 'movies'"""
    id: uuid.UUID
    imdb_rating: float | None
    genre: list[str] = Field(default_factory=list)
    title: str
    description: str | None
    director: list[str] = Field(default_factory=list)
    actors_names: list[str] = Field(default_factory=list)
    writers_names: list[str] = Field(default_factory=list)
    actors: list[ESMoviePerson] = Field(default_factory=list)
    writers: list[ESMoviePerson] = Field(default_factory=list)

class ESGenre(BaseModel):
    """Use for index 'genres'"""
    id: uuid.UUID
    name: str

class ESPersonFilms(BaseModel):
    """Films used for ESPerson"""
    model_config = ConfigDict(use_enum_values=True)
    id: uuid.UUID
    roles: list[RoleEnum]

class ESPerson(BaseModel):
    """Use for index 'persons'"""
    id: uuid.UUID
    full_name: str
    films: list[ESPersonFilms]
