# Foodgram


## Tecnhologies
Python 3.11
django 4.2
Django REST framework 3.14
Nginx
Docker
Postgres

### Set up

- Download project

- Install Docker

- Create ```.env``` file

- Fill in the env-file like it:

```text
DEBUG=False
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<Your_password>
POSTGRES_DB=foodgram
DB_ENGINE=django.db.backends.postgresql
ALLOWED_HOSTS=<Your_hosts>
DB_NAME=postgres
DB_HOST=foodgram-db
DB_PORT=5432
SECRET_KEY=<Your_project_long_string>
```

- Run docker-compose
```text
docker-compose up
```
use ```-d``` for daemon

### Additional info
You can create admin account by command

```text
docker exec -it app python manage.py createsuperuser
```
