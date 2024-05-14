from uuid import UUID

from pydantic import BaseModel

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
