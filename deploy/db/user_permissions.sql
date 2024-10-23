/*
The "uml_diagrams_api_user" role is responsible for interacting
with the database on behalf of the application itself.
This role is dedicated to the application and should be granted the minimum
necessary permissions to perform its required database operations.

See available privileges at: https://www.postgresql.org/docs/current/sql-createrole.html
*/
CREATE ROLE
    uml_diagrams_api_user
WITH
    PASSWORD 'some_secret_password'  -- password can be changed
    NOSUPERUSER
    CREATEDB
    NOCREATEROLE
    NOINHERIT
    LOGIN
    NOREPLICATION
    NOBYPASSRLS;

CREATE DATABASE 'uml_diagrams';
GRANT ALL PRIVILEGES ON DATABASE 'uml_diagrams' TO 'uml_diagrams_api_user';
GRANT ALL PRIVILEGES ON SCHEMA public TO uml_diagrams_api_user; -- should be connected to 'uml_diagrams' DB
