FROM postgres:15.0-alpine

WORKDIR /docker-entrypoint-initdb.d
COPY movies_database.ddl .
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
