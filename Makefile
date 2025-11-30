.PHONY: help install install-dev test lint format type-check clean build

help:
	@echo "pydantic-llm-io development commands:"
	@echo ""
	@echo "  make install        Install package in production mode"
	@echo "  make install-dev    Install package with dev dependencies"
	@echo "  make test           Run tests with pytest"
	@echo "  make test-cov       Run tests with coverage report"
	@echo "  make lint           Run linting (flake8, isort, black)"
	@echo "  make format         Auto-format code (black, isort)"
	@echo "  make type-check     Run mypy type checking"
	@echo "  make clean          Remove build artifacts and cache"
	@echo "  make build          Build distribution packages"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=pydantic_llm_io --cov-report=html

lint:
	flake8 src/pydantic_llm_io tests/
	isort --check-only src/pydantic_llm_io tests/
	black --check src/pydantic_llm_io tests/

format:
	isort src/pydantic_llm_io tests/
	black src/pydantic_llm_io tests/

type-check:
	mypy src/pydantic_llm_io --strict

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build
