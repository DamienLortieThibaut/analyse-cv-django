.PHONY: help build up down restart logs shell migrate test clean

COMPOSE_FILE = docker-compose.yml

help:
	@echo "Commandes disponibles :"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construire les images
	docker-compose build

up: ## Démarrer les services
	docker-compose up -d

down: ## Arrêter les services
	docker-compose down

restart: ## Redémarrer les services
	docker-compose restart

logs: ## Afficher les logs
	docker-compose logs -f

shell: ## Shell Django
	docker-compose exec web python manage.py shell

bash: ## Shell bash
	docker-compose exec web bash

migrate: ## Migrations Django
	docker-compose exec web python manage.py migrate

makemigrations: ## Créer migrations
	docker-compose exec web python manage.py makemigrations

collectstatic: ## Collecter fichiers statiques
	docker-compose exec web python manage.py collectstatic --noinput

createsuperuser: ## Créer superutilisateur
	docker-compose exec web python manage.py createsuperuser

test: ## Exécuter tests
	docker-compose exec web python manage.py test

clean: ## Nettoyer images et volumes
	docker system prune -f
	docker volume prune -f

status: ## État des conteneurs
	docker-compose ps

setup: ## Configuration initiale
	cp env.example .env
	make build
	make up
	sleep 10
	make migrate
	@echo "Configuration terminée - http://localhost:8000"