# Makefile for Automated Content Tagging Engine

.PHONY: help install install-dev run test clean docker-build docker-up docker-down db-init

help:
	@echo "Automated Content Tagging Engine - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install dependencies"
	@echo "  make install-dev      Install with dev dependencies"
	@echo "  make db-init          Initialize database"
	@echo ""
	@echo "Development:"
	@echo "  make run              Run development server"
	@echo "  make test             Run test suite"
	@echo "  make clean            Clean up generated files"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-up        Start Docker services"
	@echo "  make docker-down      Stop Docker services"

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio black pylint
	python -m spacy download en_core_web_sm

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --tb=short

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/ .coverage htmlcov/ build/ dist/ *.egg-info/

db-init:
	python database.py

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "Services starting. Wait a moment for database initialization..."
	@sleep 5
	docker-compose logs app

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f app

lint:
	pylint app/ tests/ --disable=missing-docstring --disable=too-few-public-methods
