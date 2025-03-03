.EXPORT_ALL_VARIABLES:

# General project settings
PROJECT_NAME = uml-diagrams
# DB
DB_CONTAINER_NAME = $(PROJECT_NAME)-postgres
DB_USER = postgres
DB_NAME = postgres
# API
API_IMAGE_NAME = $(PROJECT_NAME)-api
API_CONTAINER_NAME = $(PROJECT_NAME)-api
# Build settings
DOCKER_BUILDKIT = 1
BUILDKIT_PROGRESS = plain


# Docker compose
docker-compose-up:
	sudo docker compose up -d

docker-compose-up-no-logs:
	sudo docker compose up -d \
		--scale grafana=0 \
		--scale loki=0 \
		--scale promtail=0

docker-compose-down:
	sudo docker compose -p $$PROJECT_NAME down

docker-compose-stop:
	sudo docker compose -p $$PROJECT_NAME stop

docker-compose-stop-logs:
	sudo docker compose -p $$PROJECT_NAME stop grafana loki promtail

docker-compose-restart:
	sudo docker compose -p $$PROJECT_NAME restart

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

docker-download-api:
	sudo docker load -i $$API_IMAGE_NAME.tar
