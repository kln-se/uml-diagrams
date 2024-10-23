FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

# Remove unnecessary package data
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/* && \
    rm -rf /var/log/apt && \
    rm -rf /root/.cache

# Copy project to current working directory
COPY . .

ENV DJANGO_READ_ENV_FILE=False
ENV DJANGO_DEBUG_MODE=False
# DB_HOST is set to PostgreSQL container name to be able to use it by the app via docker network
ENV DB_HOST=uml-diagrams-postgres-db

STOPSIGNAL SIGINT

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

# WSGI application should be named as 'config.wsgi' because wsgi.py is located in config directory
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "180", "config.wsgi"]
