.EXPORT_ALL_VARIABLES:

# General project settings
PROJECT_NAME = uml-diagrams
NETWORK_NAME = uml_diagrams_net
# DB
DB_CONTAINER_NAME = uml-diagrams-postgres
DB_USER = postgres
DB_NAME = db.postgresql.uml-diagrams
# API
API_IMAGE_NAME = uml-diagrams-api
API_CONTAINER_NAME = uml-diagrams-api
# Build settings
DOCKER_BUILDKIT = 1
BUILDKIT_PROGRESS = plain


# Docker compose
docker-compose-up:
	sudo docker compose up -d

docker-compose-down:
	sudo docker compose -p $$PROJECT_NAME down

docker-compose-stop:
	sudo docker compose -p $$PROJECT_NAME stop

docker-compose-restart:
	sudo docker compose restart

docker-compose-del:
	sudo docker compose -p $$PROJECT_NAME down -v --rmi local


# Postgres
docker-shell-postgres:
	sudo docker exec -it $$DB_CONTAINER_NAME bash

docker-psql-postgres:
	sudo docker exec -it $$DB_CONTAINER_NAME psql -U $$DB_USER -d $$DB_NAME


# API
docker-shell-api:
	sudo docker exec -it $$API_CONTAINER_NAME bash

docker-load-api:
	sudo docker load -i $$API_IMAGE_NAME.tar
