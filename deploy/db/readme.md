#### 0. Configure PostgreSQL roles / users permissions
To interact with the database on behalf of the application, it's necessary to create a dedicated user account `uml_diagrams_api_user`, rather than using the default superuser.
This is because superuser accounts have elevated permissions that could pose a security risk if misused by the application.
To set up the appropriate permissions for the `uml-diagrams-api-user`, you can use a script `user_permissions.sql` to downgrade its certain default permissions.

Additionally, separate superuser account is created, with the `postgres` username and password by default (**should be changed** in `user_permissions.sql`), for administrative tasks.
Keep these superuser credentials secure.

**After the script is executed, you will not be able to log in to the database via `uml_diagrams_api_user` in psql anymore.
For this purpose, yous should use created superuser account in the future.**

#### 1. Copy `user_permissions.sql` script to the postgres docker container
To update user permissions using `user_permissions.sql` script you can manually copy it
from `.../uml-diagrams/deploy/db` to the postgres docker container to the directory `/usr/local/share`
with the following command:
```shell
docker cp deploy/db/user_permissions.sql uml-diagrams-postgres-db:/usr/local/share
```
#### 2. Then connect to the docker container with the following command which will run the script instantly:
```shell
docker exec -it uml-diagrams-postgres-db psql -U uml_diagrams_api_user -d postgres -f /usr/local/share/user_permissions.sql
```
Before proceeding, you can change the `user_permissions.sql` script to your needs, e.g. *superuser password* or *name*.

#### 3. Or you can use the commands below to do it manually.
Connect to the docker container (Linux):
```shell
make docker-shell-postgres
```
Connect to the docker container (Windows):
```shell
./deploy/docker-script.ps1 docker-shell-postgres
```

Inside to docker container connect to **psql** shell using `uml_diagrams_api_user` role:
```shell
psql -U uml_diagrams_api_user -d postgres
```
And use the command below to run the script:
```psql
\i /usr/local/share/user_permissions.sql
```
