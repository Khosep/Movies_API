from dataclasses import dataclass
from datetime import datetime, date
from uuid import UUID


@dataclass
class Filmwork:
    id: UUID
    title: str
    description: str
    creation_date: date
    rating: float
    type: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Genre:
    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Person:
    id: UUID
    full_name: str
    created_at: datetime
    updated_at: datetime


@dataclass
class GenreFilmwork:
    id: UUID
    genre_id: UUID
    film_work_id: UUID
    created_at: datetime


@dataclass
class PersonFilmwork:
    id: UUID
    person_id: UUID
    film_work_id: UUID
    role: str
    created_at: datetime


map_tables_sqlite_pg: dict[str, dataclass] = {
    'film_work': Filmwork,
    'genre': Genre,
    'person': Person,
    'genre_film_work': GenreFilmwork,
    'person_film_work': PersonFilmwork,
}

map_types_python_sql = {
    UUID: 'TEXT',
    date: 'DATE',
    datetime: 'timestamp with time zone',
    str: 'TEXT',
    float: 'FLOAT',
}
