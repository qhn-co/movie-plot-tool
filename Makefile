# Commandes du poste et de la CI : la CI n'appelle que ces cibles.
ENV_FILE := $(if $(wildcard .env),--env-file .env,)

.PHONY: install lint typecheck test check run web db-up db-down migrate image

install:
	uv sync --all-groups
	cd webapp && npm ci

lint:
	uv run --group lint ruff check src tests
	cd webapp && npm run lint

typecheck:
	uv run --all-groups mypy
	cd webapp && npm run typecheck

test:
	uv run --group dev pytest -q
	cd webapp && npm test

# Le gate de toute PR.
check: lint typecheck test

# API locale sur :8000 (lit .env s'il existe ; base SQLite par défaut).
run:
	uv run $(ENV_FILE) movieplot migrate
	uv run $(ENV_FILE) uvicorn movieplot.api.app:create_app --factory --reload --port 8000

# Front local sur :3000, qui relaie /api vers :8000.
web:
	cd webapp && npm run dev

# PostgreSQL local, pour travailler sur la même base que la production.
db-up:
	docker compose up -d db

db-down:
	docker compose down

migrate:
	uv run $(ENV_FILE) movieplot migrate

image:
	docker build -t movieplot:local --build-arg MOVIEPLOT_COMMIT_SHA=$$(git rev-parse HEAD) .
