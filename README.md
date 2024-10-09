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
6. Apply database migrations:
```commandline
python manage.py migrate
```
7. Provide `.env` file to the project root folder with the following variables:
```env
# Django
SECRET_KEY=<some-secret-key>
DJANGO_DEBUG_MODE=True
```
8. **(Optional)** Сonfigure the CORS (Cross-Origin Resource Sharing) settings in your `settings.py` file by adding the domain(s) of your front-end application to the `CORS_ALLOWED_ORIGINS` list.
For example:
```python
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
