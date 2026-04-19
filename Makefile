SHELL := /bin/bash

up:
	docker compose up -d

down:
	docker compose down

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src
	uv run lint-imports

logs:
	docker compose logs -f backend
