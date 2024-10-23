FROM postgres:15.8

# The /docker-entrypoint-initdb.d directory is used to initialize the DB during the first launch of the container.
# All files and scripts located in the directory will be automatically executed at the first launch.
# See https://hub.docker.com/_/postgres
COPY init-user-db.sh /docker-entrypoint-initdb.d
