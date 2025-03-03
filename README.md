# 1. What's inside?

The application programming interface (API) of a web-based application which is designed to handle the processing of UML diagrams in the form of JSON.

The API supports:
- Store, retrieve, update, delete and copy created UML diagrams;
- Share UML diagrams to other users with different permissions or make them public.

# 2. How to run

## 2.1 Basic run (dev. purpose or getting started)

2.1.1. Clone the project content from the repository to desired directory:
```commandline
git clone https://github.com/<github-user>/<repository-name>.git
```

2.1.2. Create virtual environment:
```commandline
python -m venv venv
```

2.1.3. Activate created virtual environment

On Linux:
```commandline
source venv/bin/activate
```

On Windows:
```commandline
.\venv\Scripts\Activate.ps1
```

2.1.4. Install requirements:
```commandline
pip install -r requirements.txt
```

2.1.5. Provide `.env` file to the project root folder with the following variables:
```env
# Django basic
SECRET_KEY=<some-secret-key>
# Should be overridden when running container like "docker run ... -e DJANGO_DEBUG_MODE=False"
DJANGO_DEBUG_MODE=False
# Django logging
DJANGO_LOG_LEVEL=INFO

# Admin panel
# Basic superuser (admin) account for the application
SUPERUSER_EMAIL=<some-superuser-email>
SUPERUSER_PASSWORD=<some-superuser-password>

# Database general
# User role to interact with the database on behalf of the application itself
# This role is created in deploy/db/user_permissions.sql during postgres image build (see deploy/db/Dockerfile)
DB_USER=<some-username>
DB_PASSWORD=<some-password>
DB_NAME=<some-database-name>
# For local development is set as 127.0.0.1.
# For docker it will be set to the docker postgres container name via ENV var in Dockerfile and "docker run  -e DB_HOST=..." command
DB_HOST=localhost
DB_PORT=5432

# PostgreSQL
# Creating basic superuser and init. database for postgres docker container
# About postgres init env. vars see at https://hub.docker.com/_/postgres
POSTGRES_USER=<some-username>
POSTGRES_PASSWORD=<some-password>
POSTGRES_DB=<some-database-name>

# Backend
# CORS allowed host & port details for config/settings.py
CORS_ALLOWED_HOST=<some-host>
CORS_ALLOWED_ORIGIN=http://<some-host>:<some-port>

# Frontend (Optional)
# Host and port where the frontend is served, for example: http://127.0.0.1:3000/
VITE_API_URL=http://<some-host>:<some-port>/

# Logging / grafana
GF_AUTH_ANONYMOUS_ENABLED=false
GF_SECURITY_ADMIN_EMAIL=<some-email>
GF_SECURITY_ADMIN_PASSWORD=<some-password>
GF_LIVE_ALLOWED_ORIGINS=http://<some-host>:<some-port>/
```

2.1.5.1. By the default the PostgreSQL database will be used.

>[!NOTE]
>It is possible to use default SQLite database in dev. environment by running `python manage.py ...` commands with `--settings=config.settings_local` option.

The default settings file `settings.py` declares to use PostgreSQL database.

>[!NOTE]
>It is assumed that the [official postgres image](https://hub.docker.com/_/postgres) is used.

>[!IMPORTANT]
>To use PostgreSQL database, it is necessary to provide the environment variables listed above for the database connection.

2.1.5.2. Variables `SUPERUSER_EMAIL` and `SUPERUSER_PASSWORD` are used by migration script `0002_create_superuser.py` to create the superuser account for the application.
This account is used as basic admin account for the application and can be used to get access to the admin panel.

2.1.6. Apply database migrations:
```commandline
python manage.py migrate
```

2.1.7. Сonfigure the CORS (Cross-Origin Resource Sharing) settings in your `settings.py` file by adding the domain(s) of your front-end application to the `CORS_ALLOWED_ORIGINS` and `ALLOWED_HOSTS` lists.
For example:
```python
ALLOWED_HOSTS = [
    "localhost",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

>[!IMPORTANT]
>If `DEBUG` variable is set to `True` in `settings.py`, the `CORS_ALLOWED_ORIGINS` variable will be ignored.
>Otherwise, the `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` should be configured to allow access from the front-end application domain.

2.1.8. Run django project:
```commandline
python manage.py runserver <port>
```

## 2.2. Deploy

Make sure that `.env` file is configured correctly (see 2.1.5).

2.2.1 To deploy the project to the server you can use the following command:

On Linux:
```shell
make docker-compose-up
```

>[!NOTE]
>Installed [GNU Make](https://www.gnu.org/software/make/) tool is required.

On Windows:
```shell
./docker-script docker-compose-up
```

>[!NOTE]
You can also run raw docker commands to manage project docker containers without using additional tools.
Anyway, many ready-to-use commands are available in [Makefile](Makefile) or [docker-script.ps1](docker-script.ps1) in the project root directory.

2.2.2. Manual preparation (optional)

Upon the start of the application container, the `entrypoint.sh` script will be executed.
During this process, the database migrations will be automatically applied, and static files will be collected.
However, it is also possible to perform these actions manually, as follows:

2.2.2.1. Apply database migrations:
```shell
docker exec uml-diagrams-api python manage.py migrate
```

2.2.2.2. Collect static files:
```shell
docker exec uml-diagrams-api python manage.py collectstatic --noinput
```

# 3. How to use

See documentation for the API after running the project at:
- *.yaml doc:
  - `http:/<ip-address>:<port>/schema`;
- Optional UI:
  - `http:/<ip-address>:<port>/schema/swagger-ui/`;
  - `http:/<ip-address>:<port>/schema/redoc/`.
