import enum
from uuid import UUID

from pydantic import BaseModel


class RoleEnum(enum.Enum):
    actor = 'actor'
    writer = 'writer'
    director = 'director'


class PersonBase(BaseModel):
    uuid: UUID
    full_name: str


# TODO If it fails to be inherited due to cross-imports, then specify the fields explicitly
# class PersonFilms(FilmBase):
#     roles: list[RoleEnum]

class PersonFilms(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None
    roles: list[RoleEnum]


class PersonDetails(PersonBase):
    films: PersonFilms
