# Mini Social API

REST API для соціальної платформи з авторизацією, постами та системою лайків.

## Стек

- **Python 3.12** + **FastAPI**
- **PostgreSQL** + **SQLAlchemy 2.0 async** + **Alembic**
- **Redis** — кешування постів (30 сек) + rate limit лайків (30/60s)
- **Pydantic v2**
- **Docker + docker-compose**

## Архітектура

```
src/
├── users/          — реєстрація, логін, JWT
├── posts/          — CRUD постів, фільтрація, сортування
├── likes/          — лайк/анлайк, ідемпотентність, rate limit
├── redis/          — кешування і rate limiting
├── database/       — SQLAlchemy Base, engine, session
│   └── revisions/  — Alembic міграції
├── config.py       — Settings через pydantic-settings
├── dependencies.py — UOW Depends, CurrentUser Depends
├── repositories.py — базовий SQLRepository
├── unitofwork.py   — IUnitOfWork / UnitOfWork
├── router.py       — центральний APIRouter
└── main.py         — FastAPI app, middleware
```

## Патерни

**Unit of Work** — всі операції з БД проходять через `UnitOfWork`. Сервіси отримують `IUnitOfWork` через DI і самі керують транзакціями:

```python
async with uow:
    await uow.posts.create({...})
    await uow.commit()
```

**Repository** — кожна модель має свій репозиторій що наслідує `SQLRepository`. Кастомні запити додаються окремими методами.

## Запуск через Docker

```bash
# Скопіювати .env
cp .env.example .env
# Відредагувати .env (заповнити значення)

# Запустити
make up

# Або без make
docker compose up --build -d
```

Swagger UI: http://localhost:8000/docs

## Запуск локально

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Встановити DOCKERIZED=0 в .env та вказати локальні DB/Redis адреси
alembic upgrade head
python src/main.py
```

## Ендпоінти

### Auth

| Метод | URL | Опис | Auth |
|-------|-----|------|------|
| POST | `/api/v1/users/register` | Реєстрація | — |
| POST | `/api/v1/users/login` | Логін, повертає JWT | — |
| GET | `/api/v1/users/me` | Поточний користувач | ✅ |

### Posts

| Метод | URL | Опис | Auth |
|-------|-----|------|------|
| POST | `/api/v1/posts` | Створити пост | ✅ |
| GET | `/api/v1/posts` | Список постів (пагінація, фільтр, сорт) | — |
| GET | `/api/v1/posts/{id}` | Деталі поста | — |
| PUT | `/api/v1/posts/{id}` | Редагувати пост (тільки автор) | ✅ |
| DELETE | `/api/v1/posts/{id}` | Видалити пост (тільки автор) | ✅ |

**Query параметри GET /posts:**

| Параметр | Тип | За замовч. | Опис |
|---------|-----|-----------|------|
| `limit` | int | 10 | Кількість постів (макс. 100) |
| `offset` | int | 0 | Зміщення |
| `author_id` | int | null | Фільтр по автору |
| `search` | str | null | Пошук по title і content |
| `sort` | `created_at`\|`likes` | `created_at` | Поле сортування |
| `order` | `asc`\|`desc` | `desc` | Напрямок сортування |

### Likes

| Метод | URL | Опис | Auth |
|-------|-----|------|------|
| POST | `/api/v1/posts/{id}/like` | Лайкнути пост | ✅ |
| DELETE | `/api/v1/posts/{id}/like` | Забрати лайк | ✅ |

## Redis функціонал

**Кешування постів:**
- `GET /posts` кешується на 30 секунд
- Ключ включає всі параметри запиту
- Інвалідується при create/update/delete поста і при лайку

**Rate limit лайків:**
- 30 лайків / 60 секунд на користувача
- При перевищенні → `429 Too Many Requests`
- Реалізовано через Redis INCR + EXPIRE

## HTTP статуси

| Код | Ситуація |
|-----|---------|
| 200 | OK |
| 201 | Створено |
| 204 | Видалено |
| 400 | Помилка валідації |
| 401 | Неавторизований |
| 403 | Немає прав |
| 404 | Не знайдено |
| 409 | Email вже існує |
| 429 | Перевищено rate limit |

## Приклади запитів

```bash
# Реєстрація
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","username":"johndoe","email":"john@example.com","password":"secret123"}'

# Логін
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"secret123"}'

# Створити пост (TOKEN з відповіді логіну)
curl -X POST http://localhost:8000/api/v1/posts \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"My post","content":"Hello world"}'

# Список постів з фільтром
curl "http://localhost:8000/api/v1/posts?limit=5&sort=likes&order=desc&search=hello"

# Лайк
curl -X POST http://localhost:8000/api/v1/posts/1/like \
  -H "Authorization: Bearer <TOKEN>"
```

## Міграції

```bash
# Створити нову міграцію
alembic revision --autogenerate -m "description"

# Застосувати міграції
alembic upgrade head

# Відкатити останню
alembic downgrade -1
```
