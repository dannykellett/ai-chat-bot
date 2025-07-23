.PHONY: help install dev-install test lint format run-backend run-streamlit migrate clean

help:
	@echo "Available commands:"
	@echo "  install       Install production dependencies"
	@echo "  dev-install   Install all dependencies including dev"
	@echo "  test          Run tests"
	@echo "  lint          Run linting"
	@echo "  format        Format code"
	@echo "  run-backend   Run FastAPI backend"
	@echo "  run-streamlit Run Streamlit app"
	@echo "  migrate       Run database migrations"
	@echo "  clean         Clean up generated files"

install:
	uv pip install -e .

dev-install:
	uv pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v --cov=backend --cov-report=html

lint:
	ruff check backend/ tests/
	mypy backend/

format:
	ruff format backend/ tests/

run-backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run-streamlit:
	streamlit run streamlit_app/main.py

migrate:
	alembic upgrade head

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov .ruff_cache
