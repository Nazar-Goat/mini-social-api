include .env

build:
	docker compose build

up:
	docker compose up --build --force-recreate -d

up-no-build:
	docker compose up

down:
	docker compose down

restart:
	docker compose down && docker compose up --build

PYTHONPATH := $(PWD)

makemigrations:
	PYTHONPATH=$(PYTHONPATH) alembic revision --autogenerate -m "Initial migration"

migrate:
	PYTHONPATH=$(PYTHONPATH) alembic upgrade head

logs:
	docker compose logs -f $(DB_POSTGRES_HOST)

rebuild: down build up

psql:
	docker compose exec $(DB_POSTGRES_HOST) \
	psql -U $(DB_POSTGRES_USER) -d $(DB_POSTGRES_NAME)

db-tables:
	docker compose exec $(DB_POSTGRES_HOST) \
	psql -U $(DB_POSTGRES_USER) -d $(DB_POSTGRES_NAME) -c '\dt'

db-desc:
	docker compose exec $(DB_POSTGRES_HOST) \
	psql -U $(DB_POSTGRES_USER) -d $(DB_POSTGRES_NAME) -c '\d $(TABLE)'

db-dump:
	docker compose exec $(DB_POSTGRES_HOST) \
	pg_dump -U $(DB_POSTGRES_USER) $(DB_POSTGRES_NAME) > dumps/backup.sql
db-drop:
	docker compose exec $(DB_POSTGRES_HOST) \
  	psql -U postgres -d $(DB_POSTGRES_USER) \
  	-c "DROP SCHEMA public CASCADE;"