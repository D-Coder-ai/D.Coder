.PHONY: help install lint test test-unit test-integration test-e2e test-all coverage build serve clean

help:
	@echo "Available commands:"
	@echo "  make install           - Install dependencies"
	@echo "  make lint              - Run linting (ruff)"
	@echo "  make test              - Run all tests"
	@echo "  make test-unit         - Run unit tests only"
	@echo "  make test-integration  - Run integration tests only"
	@echo "  make test-e2e          - Run E2E tests only"
	@echo "  make coverage          - Run tests with coverage report"
	@echo "  make build             - Build Docker image"
	@echo "  make serve             - Start service with docker-compose"
	@echo "  make clean             - Clean build artifacts"

install:
	pip install -r requirements.txt

lint:
	ruff check src/ tests/

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-e2e:
	pytest tests/e2e -v -m e2e

test: test-unit test-integration

test-all: test-unit test-integration test-e2e

coverage:
	pytest --cov=src --cov-report=term-missing --cov-report=html

build:
	docker build -t dcoder/agent-orchestrator:latest .

serve:
	docker-compose up -d

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
