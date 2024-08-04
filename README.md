# ASYNC_API

# Адрес репозитория:
https://github.com/Khosep/Movies_API.git

## Описание проекта:
"ASYNC_API" - ассинхронный API для онлайн-кинотеатра учебного проекта
Яндекс.Практикум, состоящий из 3-x сервисов:
1. ***sqlite_to_postgres***: Cервис по перемещению данных из SQLite в Postgres.
2. ***etl***: Cервис, который забирает необходимые данные по кинопроизведениям, жанрам и персонам из Postgres (постоянно мониторит изменения), трансформирует их и добавляет в Elasticsearch.
3. ***movies_fastapi***: API (*FastAPI*), которое получает данные из Elasticsearch и кэширует в Redis.

Cервис API покрыт тестами (*pytest*).  
Проект разворачивается в docker-compose.  
Настройка окружения и зависимости - в *poetry*.

## Стек:
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![ElasticSearch](https://img.shields.io/badge/-ElasticSearch-005571?style=for-the-badge&logo=elasticsearch)](https://www.elastic.co/elasticsearch)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)

### Дополнительно:
- raw SQL
- Psycopg2-binary
- Uvicorn

### 1. Запуск проекта в контейнерах Docker

#### 1. Создать .env файл из env.example (в корневой папке)

#### 2. Запустить Docker

#### 4. Поднимаем контейнеры:
```bash
docker-compose up -d --build
```
#### 5. Локальные адреса проекта:
Главная страница
```
http://127.0.0.1/
```
Адрес API
```
http://127.0.0.1/api/v1/
```
Документация API
```
http://127.0.0.1/api/openapi/
```
