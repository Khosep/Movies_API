from uuid import UUID
from pydantic import BaseModel

class ESGenre(BaseModel):
    id: UUID
    title: str
    description: str
    #
    # #TODO Deprecated in Pydantic 2 (remove)
    # class Config:
    #     # Заменяем стандартную работу с json на более быструю
    #     json_loads = orjson.loads
    #     json_dumps = orjson_dumps