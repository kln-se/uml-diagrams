<#
.SYNOPSIS
This PowerShell script provides Docker commands for managing project containers.
.DESCRIPTION
This is a Windows PowerShell script that contains ready-to-use commands
for managing Docker containers in a Windows environment for dev. purpose to:
    - pull a PostgreSQL image;
    - run a PostgreSQL container for a project with some settings;
    - restart a PostgreSQL container;
    - stop a PostgreSQL container;
    - kill a PostgreSQL container;
    - remove a PostgreSQL container;
    - run shell in PostgreSQL container;
    - run psql in PostgreSQL container (as superuser);
    - ... etc. for api and nginx containers.

Example usage in PowerShell to run container being in the project root directory:
    ./docker-script docker-run-postgres
#>

# Vars
$PROJECT_NAME = "uml-diagrams"
$API_IMAGE_NAME = "${PROJECT_NAME}-api"
$API_CONTAINER_NAME = "${PROJECT_NAME}-api"
$API_VERSION = "1.19.3-dev"
$DB_NAME = "uml_diagrams"
# For incoming connections
$GATEWAY_EXT_PORT = 8081


# PostgreSQL
function docker-pull-postgres {
    docker pull postgres:15.8
}
function docker-build-postgres {
    docker build `
        --no-cache `
        ./deploy/db `
        --platform linux/amd64 `
        -t "${PROJECT_NAME}-postgres:15.8"
}
function docker-run-postgres {
    docker run `
        --name "${PROJECT_NAME}-postgres" `
        --env-file .env `
        -v "${PROJECT_NAME}_pg_db_data:/var/lib/postgresql/data" `
        --net "${PROJECT_NAME}_net" `
        -p 5432:5432 `
        -d "${PROJECT_NAME}-postgres:15.8"
}
function docker-restart-postgres {
    docker restart "${PROJECT_NAME}-postgres"
}
function docker-stop-postgres {
    docker stop "${PROJECT_NAME}-postgres"
}
function docker-kill-postgres {
    docker kill "${PROJECT_NAME}-postgres"
}
function docker-remove-postgres {
    $confirmation = Read-Host "WARN: should the resources (volume and network) associated with the container also be deleted? Proceed [y/n]?"
    if ($confirmation -eq 'y') {
        docker rm "${PROJECT_NAME}-postgres";
        docker volume rm "${PROJECT_NAME}_pg_db_data";
        docker network rm "${PROJECT_NAME}_net";
    } else {
        docker rm "${PROJECT_NAME}-postgres";
    }
}
function docker-shell-postgres {
    docker exec -it "${PROJECT_NAME}-postgres" bash
}
function docker-psql-postgres {
    docker exec -it "${PROJECT_NAME}-postgres" psql -U postgres -d ${DB_NAME}
}


# API
function docker-build-api {
    docker build `
        . `
        --platform linux/amd64 `
        -t ${API_IMAGE_NAME}:${API_VERSION}
}
function docker-run-api {
    docker run `
        --name ${API_CONTAINER_NAME} `
        --env-file .env `
        --net "${PROJECT_NAME}_net" `
        -v "${PROJECT_NAME}_static:/app/staticfiles" `
        -e "DB_HOST=${PROJECT_NAME}-postgres" `
        -e DJANGO_DEBUG_MODE=False `
        -p 8000:8000 `
        -d ${API_IMAGE_NAME}:${API_VERSION}
}
function docker-restart-api {
    docker restart ${API_CONTAINER_NAME}
}
function docker-stop-api {
    docker stop ${API_CONTAINER_NAME}
}
function docker-kill-api {
    docker kill ${API_CONTAINER_NAME}
}
function docker-remove-api {
    $confirmation = Read-Host "WARN: should the resources (volume and network) associated with the container also be deleted? Proceed [y/n]?"
    if ($confirmation -eq 'y') {
        docker rm ${API_CONTAINER_NAME};
        docker volume rm "${PROJECT_NAME}_static";
        docker network rm "${PROJECT_NAME}_net";
    } else {
        docker rm ${API_CONTAINER_NAME};
    }

}
function docker-shell-api {
    docker exec -it ${API_CONTAINER_NAME} bash
}
function docker-save-api {
    docker save -o "${API_IMAGE_NAME}.tar" ${API_IMAGE_NAME}:${API_VERSION};
    echo "INFO: api image saved as '${API_IMAGE_NAME}.tar'"
}
function docker-load-api {
    docker load -i "${API_IMAGE_NAME}.tar";
    echo "INFO: api image loaded from '${API_IMAGE_NAME}.tar'"
}


# Nginx
function docker-build-nginx {
    docker build `
        --no-cache `
        ./deploy/nginx `
        --platform linux/amd64 `
        -t "${PROJECT_NAME}-nginx:latest"
}
function docker-run-nginx {
    docker run `
        --name "${PROJECT_NAME}-nginx" `
        --net "${PROJECT_NAME}_net" `
        -v "${PROJECT_NAME}_static:/staticfiles" `
        -p ${GATEWAY_EXT_PORT}:80 `
        -d "${PROJECT_NAME}-nginx:latest"
}
function docker-restart-nginx {
    docker restart "${PROJECT_NAME}-nginx"
}
function docker-stop-nginx {
    docker stop "${PROJECT_NAME}-nginx"
}
function docker-kill-nginx {
    docker kill "${PROJECT_NAME}-nginx"
}
function docker-remove-nginx {
    docker rm "${PROJECT_NAME}-nginx";
    echo "WARN: app static files volume 'uml_diagrams_static' should be removed manually (e.g. `docker volume rm uml_diagrams_static`).";
    echo "WARN: docker network 'uml-diagrams_net' should be removed manually (e.g. `docker network rm uml-diagrams_net`)."
}
function docker-shell-nginx {
    docker exec -it "${PROJECT_NAME}-nginx" bash
}


# Common
function docker-create-vols {
    docker volume create "${PROJECT_NAME}_pg_db_data";
    docker volume create "${PROJECT_NAME}_static";
    docker volume create "${PROJECT_NAME}_django_logs";
    docker volume create "${PROJECT_NAME}_grafana_data";
    docker volume create "${PROJECT_NAME}_loki_data"
}
function docker-remove-vols {
    docker volume rm "${PROJECT_NAME}_pg_db_data";
    docker volume rm "${PROJECT_NAME}_static";
    docker volume rm "${PROJECT_NAME}_django_logs";
    docker volume rm "${PROJECT_NAME}_grafana_data";
    docker volume rm "${PROJECT_NAME}_loki_data"
}
function docker-create-net {
    docker network create "${PROJECT_NAME}_net"
}
function docker-remove-net {
    docker network rm "${PROJECT_NAME}_net"
}


# Compose
function docker-compose-up {
    docker-compose up -d
}
function docker-compose-up-no-logs {
    docker-compose up -d `
    --scale grafana=0 `
    --scale loki=0 `
    --scale promtail=0
}
function docker-compose-down {
    docker-compose -p ${PROJECT_NAME} down
}
function docker-compose-stop {
    docker-compose -p ${PROJECT_NAME} stop
}
function docker-compose-restart {
    docker-compose -p ${PROJECT_NAME} restart
}
function docker-compose-del {
    docker-compose -p ${PROJECT_NAME} down -v --rmi local
}
function docker-compose-stop-logs {
    docker-compose -p ${PROJECT_NAME} stop grafana loki promtail
}


$target = $args[0]
switch ($target) {
    # PostgreSQL
    "docker-pull-postgres" {
        docker-pull-postgres
    }
    "docker-build-postgres" {
        docker-build-postgres
    }
    "docker-run-postgres" {
        docker-create-net;
        docker-run-postgres;
        if ($LASTEXITCODE -eq 0) {
            Write-Host "INFO: waiting 10 seconds for the database to start...";
            Start-Sleep -Seconds 10;
            Write-Host "INFO: applying database migrations...";
            python manage.py migrate --settings=config.settings;
        }
    }
    "docker-restart-postgres" {
        docker-restart-postgres
    }
    "docker-stop-postgres" {
        docker-stop-postgres
    }
    "docker-kill-postgres" {
        docker-kill-postgres
    }
    "docker-remove-postgres" {
        docker-stop-postgres;
        docker-remove-postgres
    }
    "docker-shell-postgres" {
        docker-shell-postgres
    }
    "docker-psql-postgres" {
        docker-psql-postgres
    }
    "docker-build-api" {
        docker-build-api
    }
    # API
    "docker-run-api" {
        docker-run-api
    }
    "docker-restart-api" {
        docker-restart-api
    }
    "docker-stop-api" {
        docker-stop-api
    }
    "docker-kill-api" {
        docker-kill-api
    }
    "docker-remove-api" {
        docker-stop-api;
        docker-remove-api
    }
    "docker-shell-api" {
        docker-shell-api
    }
    "docker-save-api" {
        docker-save-api
    }
    "docker-load-api" {
        docker-load-api
    }
    # Nginx
    "docker-build-nginx" {
        docker-build-nginx
    }
    "docker-run-nginx" {
        docker-run-nginx
    }
    "docker-restart-nginx" {
        docker-restart-nginx
    }
    "docker-stop-nginx" {
        docker-stop-nginx
    }
    "docker-kill-nginx" {
        docker-kill-nginx
    }
    "docker-remove-nginx" {
        docker-stop-nginx;
        docker-remove-nginx
    }
    "docker-shell-nginx" {
        docker-shell-nginx
    }
    # Common
    "docker-create-vols" {
        docker-create-vols
    }
    "docker-remove-vols" {
        docker-remove-vols
    }
    "docker-create-net" {
        docker-create-net
    }
    "docker-remove-net" {
        docker-remove-net
    }
    # Compose
    "docker-compose-up" {
        docker-compose-up
    }
    "docker-compose-down" {
        docker-compose-down
    }
    "docker-compose-stop" {
        docker-compose-stop
    }
    "docker-compose-restart" {
        docker-compose-restart
    }
    "docker-compose-del" {
        docker-compose-del
    }
    "docker-compose-rebuild" {
        docker-compose -p ${PROJECT_NAME} -v down;
        docker-compose build --no-cache
    }
    "docker-compose-up-no-logs" {
        docker-compose-up-no-logs
    }
    "docker-compose-stop-logs" {
        docker-compose-stop-logs
    }
    default {
        Write-Host "WARN: invalid target: $target";
        Write-Host "WARN: maybe you meant 'docker-compose-<cmd>' or 'docker-<cmd>-<service_name>' command?"
    }
}
