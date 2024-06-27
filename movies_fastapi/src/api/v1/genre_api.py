from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from services.genre_service import GenreService, get_genre_service
from .schemas.genre_schema import GenreBase
from .schemas.query_params import PageParam

router = APIRouter()


@router.get('',
            response_model=list[GenreBase],
            summary='List of genres',
            description='List of genres with pagination',
            )
async def genre_list(
        genre_service: Annotated[GenreService, Depends(get_genre_service)],
        query_params: Annotated[PageParam, Depends()],
) -> list[GenreBase]:
    genres = await genre_service.get_genres_list(query_params)
    if not genres:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Genres not found')
    return genres
