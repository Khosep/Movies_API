"""
Использование е методах endpoint:
Вместо перечисления на несколько строк page_number, page_size, sort, genre и т.д
в функцию вставляем
'query_params: Annotated[FilmListParam, Depends(FilmListParam)]'
И потом в функции используем через точку (Например, query_params.page_number)
"""

import enum
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict

from core.config import app_settings


class SortRating(str, enum.Enum):
    ASC = 'imdb_rating'
    DESC = '-imdb_rating'


class PageParam(BaseModel):
    page_number: Annotated[int, Query(default=1, ge=1, description='Номер страницы')]
    page_size: Annotated[int, Query(app_settings.page_size, ge=1, description='Количество записей на странице')]


class FilmListParam(PageParam):
    model_config = ConfigDict(use_enum_values=True)

    sort: Annotated[SortRating | None, Query(SortRating.DESC.value, description='Поле сортировки')]
    genre_name: Annotated[str | None, Query(None, description='Фильтрация по жанру')]
    # genre: Annotated[UUID | None, Query(None, description='Фильтрация по жанру')]


class SearchParam(PageParam):
    query: Annotated[str | None, Query(..., description='Строка запроса для поиска фильмов')]


class FilmTotalParam(SearchParam, FilmListParam):
    pass
