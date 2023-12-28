from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends

from .schemas.film_schema import FilmBase, FilmDetails
from ...services.film_service import FilmService, get_film_service

router = APIRouter()



@router.get('',
            response_model=list[FilmBase],
            summary='List of films',
            description='List of films with pagination, filtering by genre and sorting by rating',
            )
async def film_list(
        film_service: Annotated[FilmService, Depends(get_film_service)],
        query_params: Annotated[FilmListParams, Depends()]
) -> list[FilmBase]:
    #TODO Реализовать
    films = await film_service.get_list(query_params)
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Films not found')
    return [FilmBase(**film) for film in films]


@router.get('/{film_id}',
            response_model=FilmDetails,
            summary='Film information',
            description='Full information about the film by its id',
            )
async def film_details(
        film_id: str,
        film_service: Annotated[FilmService, Depends(get_film_service)],
) -> FilmDetails:
    #TODO Проверить
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found')

    return FilmDetails(**film)


@router.get('/search',
            response_model=list[FilmBase],
            summary='Film search',
            description='Search for films based on the words from the title',
            )
async def film_search(
        film_service: Annotated[FilmService, Depends(get_film_service)],
        query_params: Annotated[SearchParams, Depends()]
) -> list[FilmBase]:
    #TODO Реализовать
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found')

    return [FilmBase(**film) for film in films]

#TODO Проблема в том, что на выходе должны быть uuid - либо переводить в другой формат здесь,
# либо менять загрузку в индексы (на uuid)





