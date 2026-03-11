
default:
    uv run uvicorn app.main:app --reload

migrate:
    uv run alembic upgrade head

makemigrations REV +MESSAGE:
    uv run alembic revision --autogenerate --rev-id {{REV}} -m "{{MESSAGE}}"
    
format:
    uv run ruff check --select I --fix
    uv run ruff format .
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete