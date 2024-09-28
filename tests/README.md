## Тесты API

### Вариант А. Локально
#### 1) Устанавливаем локальный режим:
В файле tests/.env устанавливаем TEST_DOCKER_MODE = false (либо просто удаляем эту переменную)
#### 2) Запуск в докере тестируемых приложений (в папке tests)
```bash
docker-compose -f docker-compose_local_tests.yml up -d
```
#### 3) Стартуем тесты (в папке tests) в терминале
```bash
pytest
```
___
### Вариант Б. Запуск tests в docker
#### 1) Устанавливаем НЕлокальный режим:
В файле tests/.env устанавливаем TEST_DOCKER_MODE = true
#### 2) Запуск в докере тестов
```bash
docker-compose -f docker-compose_tests.yml up --abort-on-container-exit --exit-code-from tests
```
либо более наглядно:
```bash
docker-compose -f docker-compose_tests.yml up --abort-on-container-exit --exit-code-from tests && docker-compose -f docker-compose_tests.yml logs tests
```
Пояснение:

_--abort-on-container-exit_ - Останавливает все контейнеры, если какой-либо контейнер был остановлен. Несовместимо с -d

_--exit-code-from tests_ - Возвращает код завершения контейнера 'tests'. Подразумевает --abort-on-container-exit  
(На самом деле в данном случае будет работать и без этого ключа)

(Подробнее: https://docs.docker.com/reference/cli/docker/compose/up/)
___
### ВАЖНО: Все команды запускаем из папки tests!