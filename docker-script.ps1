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
    - ... etc. for app and nginx containers.

Example usage in PowerShell to run container being in the project root directory:
    ./docker-script docker-run-postgres
#>

# Vars
$IMAGE_NAME = "uml-diagrams-api"
$CONTAINER_NAME = "uml-diagrams-api"
$APP_VERSION = "latest"
# For incoming connections
$EXT_PORT = 8081


# PostgreSQL
function docker-pull-postgres {
    docker pull postgres:15.8
}
function docker-build-postgres {
    docker build `
        --no-cache `
        ./deploy/db `
        --platform linux/amd64 `
        -t uml-diagrams-postgres:15.8
}
function docker-run-postgres {
    docker run `
        --name uml-diagrams-postgres `
        --env-file .env `
        -v uml_diagrams_pg_db_data:/var/lib/postgresql/data `
        --net uml_diagrams_net `
        -p 5432:5432 `
        -d uml-diagrams-postgres:15.8
}
function docker-restart-postgres {
    docker restart uml-diagrams-postgres
}
function docker-stop-postgres {
    docker stop uml-diagrams-postgres
}
function docker-kill-postgres {
    docker kill uml-diagrams-postgres
}
function docker-remove-postgres {
    docker rm uml-diagrams-postgres;
    echo "WARN: postgres data volume 'uml_diagrams_pg_db_data' should be removed manually (e.g. `docker volume rm uml_diagrams_pg_db_data`).";
    echo "WARN: docker network 'uml_diagrams_net' should be removed manually (e.g. `docker network rm uml_diagrams_net`)."
}
function docker-shell-postgres {
    docker exec -it uml-diagrams-postgres bash
}
function docker-psql-postgres {
    docker exec -it uml-diagrams-postgres psql -U postgres -d db.postgresql.uml-diagrams
}


# App
function docker-build-app {
    docker build `
        . `
        --platform linux/amd64 `
        -t ${IMAGE_NAME}:${APP_VERSION}
}
function docker-run-app {
    docker run `
        --name ${CONTAINER_NAME} `
        --env-file .env `
        --net uml_diagrams_net `
        -v uml_diagrams_static:/app/staticfiles `
        -e DB_HOST=uml-diagrams-postgres `
        -e DJANGO_DEBUG_MODE=True `
        -p 8000:8000 `
        -d ${IMAGE_NAME}:${APP_VERSION}
}
function docker-restart-app {
    docker restart ${CONTAINER_NAME}
}
function docker-stop-app {
    docker stop ${CONTAINER_NAME}
}
function docker-kill-app {
    docker kill ${CONTAINER_NAME}
}
function docker-remove-app {
    docker rm ${CONTAINER_NAME};
    echo "WARN: app static files volume 'uml_diagrams_static' should be removed manually (e.g. `docker volume rm uml_diagrams_static`).";
    echo "WARN: docker network 'uml_diagrams_net' should be removed manually (e.g. `docker network rm uml_diagrams_net`)."
}
function docker-shell-app {
    docker exec -it ${CONTAINER_NAME} bash
}


# Nginx
function docker-build-nginx {
    docker build `
        --no-cache `
        ./deploy/nginx `
        --platform linux/amd64 `
        -t uml-diagrams-nginx:latest
}
function docker-run-nginx {
    docker run `
        --name uml-diagrams-nginx `
        --net uml_diagrams_net `
        -v uml_diagrams_static:/staticfiles `
        -p ${EXT_PORT}:80 `
        -d uml-diagrams-nginx:latest
}
function docker-restart-nginx {
    docker restart uml-diagrams-nginx
}
function docker-stop-nginx {
    docker stop uml-diagrams-nginx
}
function docker-kill-nginx {
    docker kill uml-diagrams-nginx
}
function docker-remove-nginx {
    docker rm uml-diagrams-nginx;
    echo "WARN: app static files volume 'uml_diagrams_static' should be removed manually (e.g. `docker volume rm uml_diagrams_static`).";
    echo "WARN: docker network 'uml_diagrams_net' should be removed manually (e.g. `docker network rm uml_diagrams_net`)."
}
function docker-shell-nginx {
    docker exec -it uml-diagrams-nginx bash
}


# Common
function docker-create-vols {
    docker volume create uml_diagrams_pg_db_data;
    docker volume create uml_diagrams_static
}
function docker-remove-vols {
    docker volume rm uml_diagrams_pg_db_data;
    docker volume rm uml_diagrams_static
}
function docker-create-net {
    docker network create uml_diagrams_net
}
function docker-remove-net {
    docker network rm uml_diagrams_net
}


# Compose
function docker-compose-up {
    docker-compose --env-file .env up -d
}
function docker-compose-del {
    docker-compose -p uml-diagrams down -v --rmi local;
    docker network rm -f uml_diagrams_net
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
        docker-run-postgres
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
        docker-remove-postgres
    }
    "docker-shell-postgres" {
        docker-shell-postgres
    }
    "docker-psql-postgres" {
        docker-psql-postgres
    }
    "docker-build-app" {
        docker-build-app
    }
    # App
    "docker-run-app" {
        docker-run-app
    }
    "docker-restart-app" {
        docker-restart-app
    }
    "docker-stop-app" {
        docker-stop-app
    }
    "docker-kill-app" {
        docker-kill-app
    }
    "docker-remove-app" {
        docker-remove-app
    }
    "docker-shell-app" {
        docker-shell-app
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
    "docker-compose-del" {
        docker-compose-del
    }
    default {
        Write-Host "Invalid target: $target"
    }
}
