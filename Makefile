.PHONY: setup up down lint test

setup:
	uv sync
	uv run pre-commit install
	uv run python -c "from pathlib import Path; import shutil; p = Path('.env'); p.exists() or shutil.copy('.env.example', p)"

up:
	docker compose up -d --wait

down:
	docker compose down

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest -v
