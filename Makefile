.PHONY: help build up down logs clean install test

help:
	@echo "RAG SDK - Makefile команды"
	@echo ""
	@echo "  make build    - Собрать Docker образы"
	@echo "  make up       - Запустить сервисы"
	@echo "  make down     - Остановить сервисы"
	@echo "  make logs     - Показать логи"
	@echo "  make clean    - Удалить все данные (включая volumes)"
	@echo "  make install  - Установить зависимости локально"
	@echo "  make test     - Запустить тесты"
	@echo "  make restart  - Перезапустить сервисы"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf uploads/*
	rm -f *.log

install:
	pip install -r requirements.txt
	pip install -r llm_manager/requirements.txt

test:
	python -m pytest tests/ -v

restart: down up

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

