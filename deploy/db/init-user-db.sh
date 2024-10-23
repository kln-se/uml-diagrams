#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER $DB_USER
    WITH
	      ENCRYPTED PASSWORD '$DB_PASSWORD'
	      NOSUPERUSER
        CREATEDB
        NOCREATEROLE
        NOINHERIT
        LOGIN
        NOREPLICATION
        NOBYPASSRLS;
	  CREATE DATABASE $DB_NAME;
	  GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOSQL

# Grant all privileges on schema public (connected to DB, created by above)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
    GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;
EOSQL
