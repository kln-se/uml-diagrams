/* Example of creating superuser role to manage the database. */
CREATE ROLE
    postgres  -- default name can be changed
WITH
    PASSWORD 'postgres'  -- default password should be changed
    SUPERUSER
    CREATEDB
    CREATEROLE
    LOGIN
    REPLICATION
    BYPASSRLS;


/*
The "uml_diagrams_api_user" role is responsible for interacting
with the database on behalf of the application itself.
This role is dedicated to the application and should be granted the minimum
necessary permissions to perform its required database operations.

Before proceeding, please ensure that there is another superuser role (or create it by
example above) before proceeding to lower the privileges of application user role.

See about privileges details: https://www.postgresql.org/docs/current/sql-createrole.html
*/
ALTER ROLE uml_diagrams_api_user
    NOSUPERUSER
    NOCREATEDB
	NOCREATEROLE
	NOINHERIT
	NOLOGIN
	NOREPLICATION
	NOBYPASSRLS;


/* List users. */
SELECT *
FROM pg_roles;
