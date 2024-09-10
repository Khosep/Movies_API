from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends, Request

from services.person_service import PersonService, get_person_service
from .schemas.film_schema import FilmBase, FilmDetails
from services.film_service import FilmService, get_film_service
from .schemas.person_schema import PersonDetails
from .schemas.query_params import SearchParam

router = APIRouter()


@router.get('/exact_search/{person_id}',
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


@router.get('/exact_search/name/{full_name}',
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


@router.get('/search',
            response_model=list[PersonDetails],
            summary='Person fuzzy search',
            description='Search for persons based on the words from the full name',
            )
async def person_search(
        person_service: Annotated[PersonService, Depends(get_person_service)],
        query_params: Annotated[SearchParam, Depends()],
) -> list[PersonDetails]:
    persons = await person_service.get_persons_by_search(query_params)
    if not persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Persons not found')

    return persons
