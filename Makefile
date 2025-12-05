.PHONY: help build up down logs shell db-shell restart clean

help:
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs from all services"
	@echo "  make logs-app       - View logs from app service"
	@echo "  make logs-mysql     - View logs from mysql service"
	@echo "  make shell          - Enter app container shell"
	@echo "  make db-shell       - Enter MySQL shell"
	@echo "  make clean          - Remove all containers and volumes"
	@echo "  make backup         - Backup database"
	@echo "  make restore        - Restore database from backup"

build:
	docker-compose build --no-cache

up:
	docker-compose up -d
	@echo "Services started. Access the app at http://localhost:8000"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

logs-mysql:
	docker-compose logs -f mysql

shell:
	docker-compose exec app bash

db-shell:
	docker-compose exec mysql mysql -u gangganghao -p gangganghao

clean:
	docker-compose down -v
	@echo "All containers and volumes removed"

backup:
	@mkdir -p backups
	docker-compose exec mysql mysqldump -u gangganghao -p gangganghao gangganghao > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up to backups/"

restore:
	@read -p "Enter backup file name: " backup_file; \
	docker-compose exec -T mysql mysql -u gangganghao -p gangganghao gangganghao < $$backup_file
	@echo "Database restored"

ps:
	docker-compose ps

status:
	@echo "=== Docker Containers ===" && \
	docker-compose ps && \
	echo "\n=== Network ===" && \
	docker network ls | grep gangganghao && \
	echo "\n=== Volumes ===" && \
	docker volume ls | grep gangganghao
