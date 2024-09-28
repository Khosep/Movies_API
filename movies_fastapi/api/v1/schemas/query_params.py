"""
Использование е методах endpoint:
Вместо перечисления на несколько строк page_number, page_size, sort, genre и т.д
в функцию вставляем
'query_params: Annotated[FilmListParam, Depends(FilmListParam)]'
И потом в функции используем через точку (Например, query_params.page_number)
"""

import enum
from typing import Annotated

from core.config import app_settings
from fastapi import Query
from pydantic import BaseModel, ConfigDict


class SortRating(str, enum.Enum):
    ASC = 'imdb_rating'
    DESC = '-imdb_rating'


class PageParam(BaseModel):
    page_number: Annotated[int, Query(default=1, ge=1, description='Номер страницы')]
    page_size: Annotated[int, Query(app_settings.page_size, ge=1, description='Количество записей на странице')]


class GenreNameFilter(BaseModel):
    genre_name: Annotated[str | None, Query(None, description='Фильтрация по жанру')]


class FilmListParam(PageParam, GenreNameFilter):
    model_config = ConfigDict(use_enum_values=True)

    sort: Annotated[SortRating | None, Query(SortRating.DESC.value, description='Поле сортировки')]


class SearchParam(PageParam):
    query: Annotated[str | None, Query(..., min_length=1, description='Строка запроса для поиска')]


class FilmTotalParam(SearchParam, GenreNameFilter):
    sort: Annotated[SortRating | None, Query(None, description='Поле сортировки')]
