from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Request

from .schemas.film_schema import FilmBase, FilmDetails, FilmQueryExact
from services.film_service import FilmService, get_film_service
from .schemas.query_params import SearchParam

# from services.film_service import FilmService, get_film_service

router = APIRouter()

# TODO [Optional]
# Get persons for certain film (search by film title)

@router.get('/{film_id}',
            response_model=FilmDetails,
            summary='Film information',
            description='Full information about the film by its uuid',
            )
async def film_details(
        film_id: UUID,
        film_service: Annotated[FilmService, Depends(get_film_service)],
        request: Request
) -> FilmDetails:

    film = await film_service.get_film_by_uuid(film_id, request)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found')

    return film

@router.post('/',
            response_model=list[FilmDetails],
            summary='Films by its title',
            description='Full information about the film by its title',
            )
async def film_by_fields(
        film_data: FilmQueryExact,
        film_service: Annotated[FilmService, Depends(get_film_service)],
        request: Request
) -> list[FilmDetails]:

    films = await film_service.get_film_by_fields(film_data, request)
    print(f'f_api: {films=}')
    print(f'f_api: {request.url=}')
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found')

    return films







# @router.get('',
#             response_model=list[FilmBase],
#             summary='List of films',
#             description='List of films with pagination, filtering by genre and sorting by rating',
#             )
# async def film_list(
#         film_service: Annotated[FilmService, Depends(get_film_service)],
#         query_params: Annotated[FilmListParams, Depends()]
# ) -> list[FilmBase]:
#     #TODO Реализовать
#     films = await film_service.get_list(query_params)
#     if not films:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Films not found')
#     return [FilmBase(**film) for film in films]





@router.get('/search',
            response_model=list[FilmBase],
            summary='Film search',
            description='Search for films based on the words from the title',
            )
async def film_search(
        film_service: Annotated[FilmService, Depends(get_film_service)],
        query_params: Annotated[SearchParam, Depends()],
        request: Request
) -> list[FilmBase]:
    #TODO Реализовать
    films = await film_service.get_films_by_search(query_params, request)
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Films not found')

    return [FilmBase(**film) for film in films]
