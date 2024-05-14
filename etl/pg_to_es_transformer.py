from logging import Logger
from typing import Generator, Any

from pydantic import ValidationError

from etl_settings import es_settings, Index
from etl_utils import coroutine
from validation.models import (PGMovie, ESMovie, ESMoviePerson, PGMoviePerson, PGGenre, ESGenre,
                               PGPersonFilms, PGPerson, ESPerson, ESPersonFilms)

class PostgresToElasticsearchTransformer:
    def __init__(self, logger: Logger):
        self._logger = logger

    """Class for transformation data extracted from postgres db for transfer to Elasticsearch."""

    @coroutine
    def transform(self, next_node: Generator) -> Generator[dict[str, Any], dict[str, Any], None]:
        """Get data, Pass it in transformation and Send the result to the next stage"""
        while total_data_in := (yield):
            self._logger.debug('Starting to transform data')
            index_name = total_data_in['index_name']
            data = total_data_in['data']
            if index_name == list(es_settings.es_indexes_names)[Index.MOVIES.value]:
                chunk_data = self._transform_movies(data)

            elif index_name == list(es_settings.es_indexes_names)[Index.GENRES.value]:
                chunk_data = self._transform_genres(data)

            elif index_name == list(es_settings.es_indexes_names)[Index.PERSONS.value]:
                chunk_data = self._transform_persons(data)
            else:
                self._logger.error(f'There is no such index_name ({index_name})')
                raise ValidationError

            # find latest 'updated_at' in chunk of movies
            max_chunk_timestamp = max(data, key=lambda m: m['updated_at'])['updated_at']
            self._logger.debug(f'{max_chunk_timestamp=}')

            self._logger.info(f'Send {len(chunk_data)} transformed data')

            total_data_out = dict(index_name=index_name, data=chunk_data, last_updated=max_chunk_timestamp)

            next_node.send(total_data_out)

    def _transform_movies(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        chunk = []
        for row in data:
            row_in = PGMovie(**row)
            row_out = self.__transform_movie(row_in)
            chunk.append(row_out)
        return chunk

    def __transform_movie(self, movie_in: PGMovie) -> dict[str, Any]:
        """Transform movie according to Elasticsearh index schema"""
        try:
            movie_out = ESMovie(
                uuid=movie_in.id,
                title=movie_in.title,
                imdb_rating=movie_in.rating,
                description=movie_in.description,
                genres=[{'uuid': g.id, 'name': g.name} for g in movie_in.genres],
                actors=[{'uuid': a.id, 'full_name': a.full_name} for a in movie_in.actors],
                writers=[{'uuid': w.id, 'full_name': w.full_name} for w in movie_in.writers],
                directors=[{'uuid': d.id, 'full_name': d.full_name} for d in movie_in.directors],
            )
            return movie_out.model_dump()
        except ValidationError as e:
            self._logger.error(e)
            raise e

    # TODO Delete
    # @staticmethod
    # def __transform_movie_person(person_in: list[PGMoviePerson]) -> dict[str, Any]:
    #     """Create dict of person fields ('director', 'actors_names', 'writers_names', 'actors', 'writers')
    #     suitable for Elasticsearh index schema (see 'movies_index.json')."""
    #     fields = ['director', 'actors_names', 'writers_names', 'actors', 'writers']
    #     map_field = {
    #         'director': 'director',
    #         'actor': 'actors_names',
    #         'writer': 'writers_names',
    #     }
    #     person_data = {field: [] for field in fields}
    #     for p in person_in:
    #         person_data[map_field[p.person_role]].append(p.person_name)
    #         if p.person_role in ('actor', 'writer'):
    #             person_data[p.person_role + 's'].append(ESMoviePerson(id=p.person_id, name=p.person_name))
    #
    #     return person_data


    def _transform_genres(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        chunk = []
        for row in data:
            row_in = PGGenre(**row)
            row_out = ESGenre(uuid=row_in.id, name=row_in.name).model_dump()
            chunk.append(row_out)
        return chunk

    def _transform_persons(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        chunk = []
        for row in data:
            row_in = PGPerson(**row)
            row_out = self.__transform_person(row_in)
            chunk.append(row_out)
        return chunk

    def __transform_person(self, peron_in: PGPerson) -> dict[str, Any]:
        """Transform person according to Elasticsearh index schema"""
        films_data = self.__transform_person_films(peron_in.films)
        try:
            person_out = ESPerson(
                uuid=peron_in.id,
                full_name=peron_in.full_name,
                films=films_data
            )
            return person_out.model_dump()
        except ValidationError as e:
            self._logger.error(e)
            raise e

    @staticmethod
    def __transform_person_films(films_in: list[PGPersonFilms]) -> list[ESPersonFilms]:
        films_data = []
        for f in films_in:
            f_data = ESPersonFilms(
                uuid=f.film_work_id,
                title=f.title,
                imdb_rating=f.rating,
                roles=f.roles,
            )
            films_data.append(f_data)
        return films_data
