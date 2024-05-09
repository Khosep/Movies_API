# ASYNC_API

# Адрес репозитория:
https://github.com/Khosep/Movies_API.git

## Описание проекта:
"ASYNC_API" - ассинхронный API для онлайн-кинотеатра учебного проекта
Яндекс.Практикум, состоящий из двух сервисов:
1. ETL сервис, который забирает данные по кинопроизведениям, жанрам и персонам
из БД Postgres и индексирует их в Elasticsearch.
2. API на Fastapi, которое получает данные из Elasticsearch и кэширует в
Redis.
Проект организован в docker-compose.

## Стек:
- Python
- PostgreSQL
- Elasticsearch
- Redis
- Fastapi
- Git
- Docker
- Poetry
- Pre-commit
- Pydantic
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
