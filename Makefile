# General project settings
PROJECT_NAME = uml-diagrams
NETWORK_NAME = uml_diagrams_net
ENV_FILE = .env
# DB
DB_CONTAINER_NAME = uml-diagrams-postgres
DB_USER = postgres
DB_NAME = db.postgresql.uml-diagrams
# API
API_СONTAINER_NAME = uml-diagrams-api
# Build settings
DOCKER_BUILDKIT = 1
BUILDKIT_PROGRESS = plain


# Docker compose
docker-compose-up:
	docker-compose --env-file $$ENV_FILE up -d

docker-compose-down:
	docker-compose -p $$PROJECT_NAME down

docker-compose-stop:
	docker-compose -p $$PROJECT_NAME stop

docker-compose-restart:
	docker-compose restart

docker-compose-del:
	docker-compose -p $$PROJECT_NAME down -v --rmi local && docker network rm -f $$NETWORK_NAME


# Postgres
docker-shell-postgres:
	docker exec -it $$DB_CONTAINER_NAME bash

docker-psql-postgres:
	docker exec -it $$DB_CONTAINER_NAME psql -U $$DB_USER -d $$DB_NAME


# API
docker-shell-api:
	docker exec -it $$API_CONTAINER_NAME bash
