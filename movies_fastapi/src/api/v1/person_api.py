from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Request

from services.person_service import PersonService, get_person_service
from .schemas.film_schema import FilmBase, FilmDetails
from services.film_service import FilmService, get_film_service
from .schemas.person_schema import PersonDetails
from .schemas.query_params import SearchParam

# from services.film_service import FilmService, get_film_service

router = APIRouter()

# TODO full_name ('text' and 'raw keyword')
# Get persons for certain film (search by film title)

@router.get('/{person_id}',
            response_model=PersonDetails,
            summary='Get person information (exact match)',
            description='Get full information about person by its uuid',
            )
async def person_details(
        person_id: UUID,
        person_service: Annotated[PersonService, Depends(get_person_service)],
) -> PersonDetails:

    person = await person_service.get_person_by_uuid(person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Person not found')

    return person


@router.get('/name/{full_name}',
            response_model=list[PersonDetails],
            summary='Get person/s (exact match)',
            description='Get full information about person/s by full_name',
            )
async def person_by_name(
        full_name: str,
        person_service: Annotated[PersonService, Depends(get_person_service)],
) -> list[PersonDetails]:

    persons = await person_service.get_person_by_name(full_name)
    if not persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Persons not found')

    return persons

# TODO Implement
# @router.get('',
#             response_model=list[FilmBase],
#             summary='List of films',
#             description='List of films with pagination, filtering by genre and sorting by rating',
#             )
# async def film_list(
#         film_service: Annotated[FilmService, Depends(get_film_service)],
#         query_params: Annotated[FilmListParams, Depends()]
# ) -> list[FilmBase]:
#     films = await film_service.get_list(query_params)
#     if not films:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Films not found')
#     return [FilmBase(**film) for film in films]




# TODO Implement it if necessary
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
