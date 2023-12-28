--Create custom schema
CREATE SCHEMA IF NOT EXISTS content;

--Create table 'film_work'
CREATE TABLE IF NOT EXISTS content.film_work (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

--Create table 'genre'
CREATE TABLE IF NOT EXISTS content.genre (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);

--Create table 'person'
CREATE TABLE IF NOT EXISTS content.person (
    id UUID PRIMARY KEY,
    full_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);


--Create linking table 'genre_film_work'
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id UUID PRIMARY KEY,
    genre_id UUID NOT NULL,
    film_work_id UUID NOT NULL,
    CONSTRAINT unique_genre_file_work UNIQUE (genre_id, film_work_id),
    CONSTRAINT fk_genre_film_work_genre_id FOREIGN KEY (genre_id) REFERENCES content.genre(id),
    CONSTRAINT fk_genre_film_work_film_work_id FOREIGN KEY (film_work_id) REFERENCES content.film_work(id),
    created_at TIMESTAMP WITH TIME ZONE
);

--Create linking table 'person_film_work'
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id UUID PRIMARY KEY,
    person_id UUID NOT NULL,
    film_work_id UUID NOT NULL,
    role TEXT NOT NULL,
    CONSTRAINT unique_person_file_work UNIQUE (person_id, film_work_id, role),
    CONSTRAINT fk_person_film_work_person_id FOREIGN KEY (person_id) REFERENCES content.person(id),
    CONSTRAINT fk_person_film_work_film_work_id FOREIGN KEY (film_work_id) REFERENCES content.film_work(id),
    created_at TIMESTAMP WITH TIME ZONE
);

--Create indexes
CREATE UNIQUE INDEX idx_film_work_genre
       ON content.genre_film_work(film_work_id, genre_id);
CREATE UNIQUE INDEX idx_film_work_person
       ON content.person_film_work(film_work_id, person_id, role);
CREATE INDEX idx_film_work_creation_date
       ON content.film_work(creation_date);

--psql -h 127.0.0.1 -p 5432 -U postgres -d movies_database -f movies_database.ddl
