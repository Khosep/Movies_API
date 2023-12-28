from uuid import UUID

from pydantic import BaseModel


class PersonBase(BaseModel):
    uuid: UUID
    full_name: str


