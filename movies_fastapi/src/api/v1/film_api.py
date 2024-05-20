from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query

from .schemas.film_schema import FilmBase, FilmDetails, FilmQueryExact
from services.film_service import FilmService, get_film_service
from .schemas.query_params import SearchParam, FilmListParam, FilmTotalParam

# from services.film_service import FilmService, get_film_service

router = APIRouter()

# TODO [Optional]
# Get persons for certain film (search by film title)

@router.get('/exact_search/{film_id}',
            response_model=FilmDetails,
            summary='Get film information (exact match)',
            description='Get full information about the film by its uuid',
            )
async def film_details(
        film_id: UUID,
        film_service: Annotated[FilmService, Depends(get_film_service)],
) -> FilmDetails:

    film = await film_service.get_film_by_uuid(film_id)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Film not found')

    return film

@router.post('/exact_search',
            response_model=list[FilmDetails],
            summary='Get films by their fields (exact match)',
            description='Get full information about the films by their fields'
                        ' (uuid, title, imdb_rating)',
            )
async def film_by_fields(
        film_data: FilmQueryExact,
        film_service: Annotated[FilmService, Depends(get_film_service)],
) -> list[FilmDetails]:

    films = await film_service.get_film_by_fields(film_data)
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Films not found')

    return films

# TODO Problem: Validation for query params in Basemodel (film_schema.py) doesn't work properly: Error 500 instead of 422
# To resolve:
# Reason: https://fastapi.tiangolo.com/tutorial/handling-errors/?h=validationerro#requestvalidationerror-vs-validationerror
# Solution: https://github.com/tiangolo/fastapi/issues/2387#issuecomment-1276809398 (doesn't work)
# https://github.com/tiangolo/fastapi/discussions/8971
# @router.get('/exact_search',
#             response_model=list[FilmDetails],
#             summary='Get films by their fields (exact match)',
#             description='Get full information about the films by their fields'
#                         ' (uuid, title, imdb_rating)',
#             )
# async def film_by_fields2(
#         film_data: Annotated[FilmQueryExact, Depends()],
#         film_service: Annotated[FilmService, Depends(get_film_service)],
# ) -> list[FilmDetails]:
#
#     films = await film_service.get_film_by_fields(film_data)
#     if not films:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Films not found')
#
#     return films







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
            response_model=list[FilmDetails],
            summary='Film fuzzy search',
            description='Search for films based on the words from the title',
            )
async def film_search(
        film_service: Annotated[FilmService, Depends(get_film_service)],
        query_params: Annotated[FilmTotalParam, Depends()],
        # sort_and_filter_params: Annotated[FilmListParam, Depends()],
) -> list[FilmDetails]:
    #TODO Реализовать
    films = await film_service.get_films_by_search(query_params)
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Films not found')

    return [FilmDetails(**film) for film in films]
