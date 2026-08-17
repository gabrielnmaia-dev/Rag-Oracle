COMPOSE := docker compose

.PHONY: build up down logs shell dbshell makemigrations migrate createsuperuser test lint format collectstatic

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

shell:
	$(COMPOSE) exec web python manage.py shell

dbshell:
	$(COMPOSE) exec web python manage.py dbshell

makemigrations:
	$(COMPOSE) exec web python manage.py makemigrations

migrate:
	$(COMPOSE) exec web python manage.py migrate

createsuperuser:
	$(COMPOSE) exec web python manage.py createsuperuser

test:
	$(COMPOSE) exec web pytest

lint:
	$(COMPOSE) exec web ruff check .

format:
	$(COMPOSE) exec web ruff format .

collectstatic:
	$(COMPOSE) exec web python manage.py collectstatic --noinput
