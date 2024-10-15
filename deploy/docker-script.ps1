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
    - run psql in PostgreSQL container (as superuser).

Example usage in PowerShell to run container:
    ./docker-script.ps1 docker-run-postgres
Or being in the project root directory:
    ./deploy/docker-script.ps1 docker-run-postgres
#>


function docker-pull-postgres {
    docker pull postgres:15.8
}

function docker-run-postgres {
    docker run `
        --name uml-diagrams-postgres-db `
        --env-file .env `
        -v uml_diagrams_pg_db_data:/var/lib/postgresql/data `
        -p 5432:5432 `
        -d postgres:15.8
}

function docker-restart-postgres {
    docker restart uml-diagrams-postgres-db
}

function docker-stop-postgres {
    docker stop uml-diagrams-postgres-db
}

function docker-kill-postgres {
    docker kill uml-diagrams-postgres-db
}

function docker-remove-postgres {
    docker rm uml-diagrams-postgres-db
}

function docker-shell-postgres {
    docker exec -it uml-diagrams-postgres-db bash
}

function docker-psql-postgres {
    docker exec -it uml-diagrams-postgres-db psql -U postgres -d db.postgresql.uml-diagrams
}

$target = $args[0]
switch ($target) {
    "docker-pull-postgres" {
        docker-pull-postgres
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
    default {
        Write-Host "Invalid target: $target"
    }
}
