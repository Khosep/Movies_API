# MOVIES API

## Описание проекта:
Aсинхронный API для онлайн-кинотеатра *по мотивам* 3 и 4 спринтов учебного проекта
курса "Мiddlе-Pуthоn разработчик" Яндекс.Практикум , состоящий из 3-x сервисов:
1. ***sqlite_to_postgres***: Cервис по перемещению данных из SQLite в Postgres.
2. ***etl***: Cервис, который забирает необходимые данные по кинопроизведениям, жанрам и персонам из Postgres (постоянно мониторит изменения), трансформирует их и добавляет в Elasticsearch.
3. ***movies_fastapi***: API (*FastAPI*), которое получает данные из Elasticsearch и кэширует в Redis.

Cервис API покрыт тестами (*pytest*).  
Проект разворачивается в docker-compose.  

## Стек:
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![ElasticSearch](https://img.shields.io/badge/-ElasticSearch-005571?style=for-the-badge&logo=elasticsearch)](https://www.elastic.co/elasticsearch)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)
[![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)](https://www.nginx.com)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)

### Дополнительно:
- raw SQL
- Psycopg2-binary
- Uvicorn
- Pytest

## Запуск:
### 1. Запуск проекта в контейнерах Docker

#### 1) Создать .env файл из env.example (в корневой папке)

#### 2) Запустить приложение в Docker
```bash
docker-compose up -d --build
```
#### 3) Локальный адрес проекта:

http://127.0.0.1/api/openapi/

### 2. Тестирования API сервиса

#### 1) Перейти в папку *tests*
#### 2) Запустить тесты в докере
```bash
docker-compose -f docker-compose_tests.yml up --abort-on-container-exit --exit-code-from tests
```
либо более наглядно:
```bash
docker-compose -f docker-compose_tests.yml up --abort-on-container-exit --exit-code-from tests && docker-compose -f docker-compose_tests.yml logs tests
```
#### Возможен локальный запуск тестов: [Подробнее](tests/README.md)
