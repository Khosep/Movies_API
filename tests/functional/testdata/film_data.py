import uuid
from typing import Any

film_to_load = {
    'film 1': {
        'uuid': '3d825f60-9fff-4dfe-b294-1a45fa1e115d',
        'title': 'Star Wars: Episode IV - A New Hope',
        'description': 'The Imperial Forces, under orders from cruel Darth Vader...',
        'imdb_rating': 8.6,
        'genres': [
            {'name': 'Action', 'uuid': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff'},
            {
                'name': 'Adventure',
                'uuid': '120a21cf-9097-479e-904a-13dd7198c1dd',
            },
            {
                'name': 'Fantasy',
                'uuid': 'b92ef010-5e4c-4fd0-99d6-41b6456272cd',
            },
            {'name': 'Sci-Fi', 'uuid': '6c162475-c7ed-4461-9184-001ef3d9f26e'},
        ],
        'actors': [
            {
                'uuid': '26e83050-29ef-4163-a99d-b546cac208f8',
                'full_name': 'Mark Hamill',
            },
            {
                'uuid': '5b4bf1bc-3397-4e83-9b17-8b10c6544ed1',
                'full_name': 'Harrison Ford',
            },
            {
                'uuid': 'b5d2b63a-ed1f-4e46-8320-cf52a32be358',
                'full_name': 'Carrie Fisher',
            },
            {
                'uuid': 'e039eedf-4daf-452a-bf92-a0085c68e156',
                'full_name': 'Peter Cushing',
            },
        ],
        'writers': [
            {
                'uuid': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a',
                'full_name': 'George Lucas',
            },
        ],
        'directors': [
            {
                'uuid': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a',
                'full_name': 'George Lucas',
            },
        ],
    },
    'film 2': {
        'uuid': '88888888-8888-8888-8888-888888888888',
        'title': 'Film without any genres and persons',
        'description': 'The film has no known actors, directors, or writers.'
                       ' Genres are not defined either.',
        'imdb_rating': 10.0,
        'genres': [],
        'actors': [],
        'writers': [],
        'directors': [],
    },
    'film 3': {
        'uuid': '80d1bf50-ce62-43a8-b852-6f116ce4f91b',
        'title': 'Flaming Star',
        'description': 'West Texas in the years after the Civil War ...',
        'imdb_rating': 6.5,
        'genres': [
            {'name': 'Western', 'uuid': '0b105f87-e0a5-45dc-8ce7-f8632088f390'}
        ],
        'actors': [
            {
                'uuid': '55b847bd-2bed-471f-8dab-0da4ad953e30',
                'full_name': 'Barbara Eden',
            },
            {
                'uuid': '956aa2d6-9a02-422c-bd18-06ccd4e31044',
                'full_name': 'Elvis Presley',
            },
            {
                'uuid': 'e687e39e-73ad-4bdf-98d1-35babcf84135',
                'full_name': 'Dolores del Rio',
            },
            {
                'uuid': 'f6aa7f67-58ff-4dbc-ac2d-ae137594a24f',
                'full_name': 'Steve Forrest',
            },
        ],
        'writers': [
            {
                'uuid': '3ca7b12b-7537-4f18-b479-f6f34c1fc924',
                'full_name': 'Nunnally Johnson',
            },
            {
                'uuid': '6132c8ce-3744-4885-8395-3f048b3c6e71',
                'full_name': 'Clair Huffaker',
            },
        ],
        'directors': [
            {
                'uuid': 'e59ffb1a-bcf7-4adb-8b26-c7883dbe68ad',
                'full_name': 'Don Siegel',
            },
        ],
    },
    'film 4': {
        'uuid': '44444444-4444-4444-4444-444444444444',
        'title': 'film 4',
        'description': 'pass',
        'imdb_rating': 4.0,
        'genres': [
            {'name': 'Action', 'uuid': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff'},
            {
                'name': 'Fantasy',
                'uuid': 'b92ef010-5e4c-4fd0-99d6-41b6456272cd',
            },
        ],
        'actors': [],
        'writers': [],
        'directors': [],
    },
    'film 5': {
        'uuid': '55555555-5555-5555-5555-555555555555',
        'title': 'film 5',
        'description': 'pass',
        'imdb_rating': 9,
        'genres': [
            {'name': 'Action', 'uuid': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff'},
        ],
        'actors': [],
        'writers': [],
        'directors': [],
    },
}

FILM = {
    '3d825f60-9fff-4dfe-b294-1a45fa1e115d': 'film 1',
    '88888888-8888-8888-8888-888888888888': 'film 2',
    '80d1bf50-ce62-43a8-b852-6f116ce4f91b': 'film 3',
    '44444444-4444-4444-4444-444444444444': 'film 4',
    '55555555-5555-5555-5555-555555555555': 'film 5',
}

GENRE_PARAM = {
    'Action': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff',
    'Non-existent Genre': '00000000-0000-0000-0000-000000000000',
}


def get_films_to_load(
        number: int, *, title: str = 'film', rating: int = 9
) -> list[dict[str, Any]]:
    films_to_load = [
        {
            'uuid': str(uuid.uuid4()),
            'title': title,
            'description': 'The Imperial Forces, under orders from cruel Darth Vader...',
            'imdb_rating': rating,
            'genres': [
                {
                    'name': 'Action',
                    'uuid': '3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff',
                },
                {
                    'name': 'Adventure',
                    'uuid': '120a21cf-9097-479e-904a-13dd7198c1dd',
                },
                {
                    'name': 'Fantasy',
                    'uuid': 'b92ef010-5e4c-4fd0-99d6-41b6456272cd',
                },
                {
                    'name': 'Sci-Fi',
                    'uuid': '6c162475-c7ed-4461-9184-001ef3d9f26e',
                },
            ],
            'actors': [
                {
                    'uuid': '26e83050-29ef-4163-a99d-b546cac208f8',
                    'full_name': 'Mark Hamill',
                },
                {
                    'uuid': '5b4bf1bc-3397-4e83-9b17-8b10c6544ed1',
                    'full_name': 'Harrison Ford',
                },
                {
                    'uuid': 'b5d2b63a-ed1f-4e46-8320-cf52a32be358',
                    'full_name': 'Carrie Fisher',
                },
                {
                    'uuid': 'e039eedf-4daf-452a-bf92-a0085c68e156',
                    'full_name': 'Peter Cushing',
                },
            ],
            'writers': [
                {
                    'uuid': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a',
                    'full_name': 'George Lucas',
                },
            ],
            'directors': [
                {
                    'uuid': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a',
                    'full_name': 'George Lucas',
                },
            ],
        }
        for _ in range(number)
    ]
    return films_to_load
