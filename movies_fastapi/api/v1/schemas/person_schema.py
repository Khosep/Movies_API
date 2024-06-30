import enum
from uuid import UUID

from pydantic import BaseModel


class RoleEnum(enum.Enum):
    actor = 'actor'
    writer = 'writer'
    director = 'director'

class PersonName(BaseModel):
    full_name: str

class PersonBase(BaseModel):
    uuid: UUID
    full_name: str


class PersonFilms(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None
    roles: list[RoleEnum]


class PersonDetails(PersonBase):
    films: list[PersonFilms]
