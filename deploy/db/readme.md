### Configure PostgreSQL roles / users permissions
To interact with the database on behalf of the application, it's necessary to create a dedicated user account `uml_diagrams_api_user`, rather than using the default superuser.
This is because superuser accounts have elevated permissions that could pose a security risk if misused by the application.

There is two ways to configure the user permissions:
- Via Dockerfile, overriding official postgres image (by default);
- Manually inside the container over clean postgres image (optional).

As for using Dockerfile: the `uml_diagrams_api_user` role will be created by `init-user-db.sh` script used by the `deploy\db\Dockerfile` docker image.
The `init-user-db.sh` script will executed inside the postgres docker container at the first launch of the container.

### I. Via Dockerfile, overriding official postgres image (by default)
According to the `deploy/db/Dockerfile`, the script `init-user-db.sh` will be copied to `/docker-entrypoint-initdb.d` directory of the postgres docker container.
So, it will be executed automatically and the configured permissions, defined in `user_permissions.sql` will be applied.

**If you want to change the default permissions, you should change them in `user_permissions.sql` before building the database image.**

### II. Manually, inside the container over clean postgres image (optional)

You can update the desired permissions in the `delpoy/db/user_permissions.sql` script, given as an example.

#### 1. Copy `user_permissions.sql` script to the postgres docker container
To update user permissions using `user_permissions.sql` script you can manually copy it
from `.../uml-diagrams/deploy/db` to the postgres docker container to the directory `/usr/local/share`
with the following command:
```shell
docker cp deploy/db/user_permissions.sql uml-diagrams-postgres-db:/usr/local/share
```

#### 2. Then connect to the docker container with the following command which will run the script instantly
For this step it's assumed that superuser on behalf you log in (e.g. `postgres` role) has **LOGIN**, **CREATEROLE** or **SUPERUSER** privileges.
Otherwise, you should use appropriate role for the script below:
```shell
docker exec uml-diagrams-postgres-db psql -U postgres -d postgres -f /usr/local/share/user_permissions.sql
```
**Before proceeding, you can change the `user_permissions.sql` script to your needs.**

#### 2.1. Or you can use the commands below to do it manually
Connect to the docker container (Linux):
```shell
make docker-shell-postgres
```
Connect to the docker container (Windows):
```shell
./docker-script docker-shell-postgres
```
Inside to docker container connect to **psql** shell using `postgres` role:
```shell
psql -U postgres -d postgres
```
And use the command below to run the script:
```psql
\i /usr/local/share/user_permissions.sql
```
