from uuid import UUID

from pydantic import BaseModel


class GenreBase(BaseModel):
    uuid: UUID
    name: str


