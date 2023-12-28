from uuid import UUID

from pydantic import BaseModel

from movies_fastapi.src.api.v1.schemas.genre_schema import GenreBase
from movies_fastapi.src.api.v1.schemas.person_schema import PersonBase


class FilmBase(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None

class FilmDetails(FilmBase):
    description: str | None
    genre: list[GenreBase]
    actors: list[PersonBase]
    writers: list[PersonBase]
    directors: list[PersonBase]
