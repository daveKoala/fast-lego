COMPOSE := docker compose

.PHONY: help build start stop restart logs test db-init db-setup db-seed

help:
	@echo "Available targets:"
	@echo "  make build     - Build images"
	@echo "  make start     - Start services in background"
	@echo "  make stop      - Stop and remove services"
	@echo "  make restart   - Restart services"
	@echo "  make logs      - Tail API logs"
	@echo "  make test      - Run pytest in api container"
	@echo "  make db-setup  - Create database tables"
	@echo "  make db-seed   - Seed catalog data"
	@echo "  make db-init   - Create tables and seed data"

build:
	$(COMPOSE) build

start:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) down

restart: stop start

logs:
	$(COMPOSE) logs -f api

test:
	$(COMPOSE) run --rm api pytest

db-setup:
	$(COMPOSE) run --rm api python -m app.scripts.db_tasks setup

db-seed:
	$(COMPOSE) run --rm api python -m app.scripts.db_tasks seed

db-init:
	$(COMPOSE) run --rm api python -m app.scripts.db_tasks init
