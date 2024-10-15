# 1. What's inside?

The application programming interface (API) of a web-based application which is designed to handle the processing of UML diagrams in the form of JSON.

The API supports:
1. Store, retrieve, update, delete and copy created UML diagrams;
2. Share UML diagrams to other users with different permissions.

# 2. How to run

**Basic run:**
1. Proceed to the directory where the project should be placed:
```commandline
cd <path-to-directory>
```
2. Clone the project content from the repository inside this directory:
```commandline
git clone https://github.com/<github-user>/<repository-name>.git
```
3. Create virtual environment:
```commandline
python -m venv venv
```
4. Activate created virtual environment (Windows):
```commandline
.\venv\Scripts\Activate.ps1
```
5. Install requirements:
```commandline
pip install -r requirements.txt
```
6. Provide `.env` file to the project root folder with the following variables:
```env
# Django
SECRET_KEY=<some-secret-key>
DJANGO_DEBUG_MODE=True

# PostgreSQL DB: creating user interacting with the database on behalf of the application itself
# About postgres init env. vars see https://hub.docker.com/_/postgres
POSTGRES_USER=<some-username>
POSTGRES_PASSWORD=<some-password>
POSTGRES_DB=<some-database-name>
DB_HOST=127.0.0.1
DB_PORT=5432

# Basic superuser (admin) account for the application
SUPERUSER_EMAIL=<some-superuser-email>
SUPERUSER_PASSWORD=<some-superuser-password>
```
6.1. By default the PostgreSQL database will be used. *It is assumed that the official postgres image from dockerhub is used.*
So it is necessary to provide the environment variables listed above for the database connection.
To switch back to the SQLite database, it is necessary to set `default` key in the `DATABASES` dictionary in `config/settings.py` file for sqlite engine:
```python
DATABASES = {
    "postgres": {
        ...
    },
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}
```
6.2. Variables `SUPERUSER_EMAIL` and `SUPERUSER_PASSWORD` are used by migration script `0002_create_superuser.py` to create the superuser account for the application.
This account is used as basic admin account for the application and can be used to get access to the admin panel.
7. Apply database migrations:
```commandline
python manage.py migrate
```
8. **(Optional)** Сonfigure the CORS (Cross-Origin Resource Sharing) settings in your `settings.py` file by adding the domain(s) of your front-end application to the `CORS_ALLOWED_ORIGINS` and `ALLOWED_HOSTS` lists.
For example:
```python
ALLOWED_HOSTS = [
    "localhost",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```
9. Run django project:
```commandline
python manage.py runserver <port>
```

# 3. How to use

See documentation for the API after running the project at:
- *.yaml doc:
  - `http:/<ip-address>:<port>/schema`;
- Optional UI:
  - `http:/<ip-address>:<port>/schema/swagger-ui/`;
  - `http:/<ip-address>:<port>/schema/redoc/`.
