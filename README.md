# REST API для справочника организаций

Проект реализует REST API и веб-интерфейс для управления **Организациями**, **Зданиями** и **Видами деятельности**.

Стек: **FastAPI + SQLAlchemy + Pydantic + Alembic + SQLite + Docker**.

---

## Содержание

1. [Установка и запуск через Docker](#установка-и-запуск-через-docker)
2. [Структура проекта](#структура-проекта)
3. [API](#api)
4. [Веб-интерфейс](#веб-интерфейс)
5. [Миграции Alembic](#миграции-alembic)
6. [Тестовые данные](#тестовые-данные)
7. [Swagger / Redoc](#swagger--redoc)

---

## Установка и запуск через Docker

**Требования:**
- Docker
- docker-compose

**Команды для запуска:**

1. Клонируем репозиторий (или скопировать проект локально):

```bash
git clone https://github.com/AlexFenixQ/org_catalog
cd org_catalog
```

2. Собираем Docker-образ:

```bash
docker-compose build
```

3. Запускаем контейнер:

```bash
docker-compose up
```

4. Для остановки контейнера:

```bash
docker-compose down
```

## Структура проекта

```bash
alembic/
├── env.py
├── script.py.mako
└── versions/
app/
├── routers/
│   ├── activities.py  # Web для деятельностей
│   ├── api_activities.py     # JSON API для деятельностей
│   ├── api_buildings.py      # JSON API для зданий
│   ├── api_organizations.py  # JSON API для организаций
│   ├── buildings.py      # Web для зданий
│   └── organizations.py  # Web для организаций
├── templates/         # Jinja2 HTML-шаблоны
│   ├── activity_form.html  # Html-форма для деятельностей
│   ├── activity_tree.html     # Html-дерево для деятельностей
│   ├── building_form.html      # Html-форма для зданий
│   ├── building_list.html      # Html-таблица для зданий
│   ├── org_form.html  # Html-форма для организаций
│   └── org_list.html  # Html-таблица для организаций
├── main.py            # FastAPI приложение
├── models.py          # SQLAlchemy модели
├── schemas.py         # Pydantic схемы
├── deps.py            # Зависимости (get_db, verify_api_key)
├── database.py        # Настройка SQLAlchemy
└── populate_db.py     # Скрипт для тестовых данных

Dockerfile
docker-compose.yml
requirements.txt
README.md
```

## API

**Пример JSON API для организаций**

- GET /organizations/ — список всех организаций
- GET /organizations/{org_id} — информация по ID организации
- GET /organizations/by_building/{building_id} — организации в здании
- GET /organizations/by_activity/{activity_id} — организации по виду деятельности (включая дерево)
- GET /organizations/search?name= — поиск по названию
- GET /organizations/by_geo?lat=&lon=&radius_km= — поиск по координатам

**Пример запроса с API ключом:**

```bash
curl -H "x-api-key: SECRET_KEY_123" http://localhost:8000/organizations/
```

**Пример JSON API для деятельностей**

- GET /buildings/ — список зданий
- GET /buildings/{building_id} — информация по зданию

**Пример JSON API для деятельностей**

- GET /activities/ — дерево деятельностей
- GET /activities/{activity_id} — информация по деятельности
- POST /activities/new — создание деятельности
- POST /activities/edit/{activity_id} — редактирование деятельности
- GET /activities/delete/{activity_id} — удаление деятельности

## Веб-интерфейс

Доступ к веб-интерфейсу осуществляется по адресу http://localhost:8000/

- /organizations — список организаций, CRUD формы
- /buildings — список зданий, CRUD формы
- /activities — дерево деятельностей, CRUD формы

## Миграции Alembic

Для создания таблиц и схем в базе данных используем Alembic.

1. Инициализация Alembic уже выполнена (alembic/ есть)
2. Генерация миграций для всех моделей:

```bash
docker-compose run api alembic revision --autogenerate -m "initial tables"
```

3. Применение миграций:

```bash
docker-compose run api alembic upgrade head
```

После этого база org_catalog.db будет готова.

## Тестовые данные

Для наполнения базы тестовыми данными:

```bash
docker-compose run --rm api python -m data.populate_db
```

Пример добавляет:

- 2 здания
- дерево деятельностей: "Еда" → "Мясная продукция", "Молочная продукция"
- 2 организации: "ООО Рога и Копыта", "Молочный мир"

## Swagger / Redoc

FastAPI автоматически генерирует документацию:

- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

Все JSON API и методы отображаются в документации.

## Примечания

- Телефоны организаций хранятся в базе как строка через запятую и преобразуются в список при выводе через API.
- Максимальная вложенность деятельностей — 3 уровня.
- Для всех запросов JSON API требуется заголовок x-api-key: SECRET_KEY_123.
