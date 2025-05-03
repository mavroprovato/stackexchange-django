# StackExchange Django

This project implements an API for a [StackExchange](https://stackexchange.com/)-like site. The API tries to be as
faithful as possible to the [official stackexchange API](https://api.stackexchange.com/docs). Data for the application
can be loaded with the data dump available at [archive.org](https://archive.org/details/stackexchange). Those dumps
used to be updated regularly, but it seems that since April 2024, no new dumps are uploaded.

The application is built with [Django](https://www.djangoproject.com/), using [Python](https://www.python.org) and
[Poetry](https://python-poetry.org/) for dependency management. [PostgreSQL](https://www.postgresql.org/) is used as the
project database. [Redis](https://redis.io/) is used as a broker for background application tasks and as the caching
backend.

## System dependencies

In order to run the project, you need to have [Python](https://www.python.org/downloads/),
[uv](https://docs.astral.sh/uv), [PostgreSQL](https://www.postgresql.org/download/), and
[Redis](https://redis.io/) installed.

You will also need to create a PostgreSQL database in order to store the data, and a database user that will access that
database. The user needs to have the rights to create a database, in order to run the application tests. You can set up
the database by running the following commands:

```
$ sudo -u postgres psql

postgres=# CREATE USER stackexchange WITH ENCRYPTED PASSWORD 'stackexchange' CREATEDB;
postgres=# CREATE DATABASE stackexchange OWNER stackexchange;
```

You can change the database name, user and password to whatever values you wish, but you need to change the
configuration.

Then you need to create the database schema by running:

```
uv run manage.py migrate
```

## Configuration

Another prerequisite before running the application is to create an `.env` file in the project directory that will hold
the environment variables that will configure the application. A sample file that you can use as a template exists in
the root directory of the application and is named `.env.example`. The environment variables that can be set are:

* `SECRET_KEY` is the value of the [Django secret key](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-SECRET_KEY).
  The key is used to provide cryptographic signing, and should be set to a unique, unpredictable value. You can generate
  one by running `uv run python -c 'from django.core.management.utils import get_random_secret_key;print(get_random_secret_key())'`
* `DB_HOST` is the name of the host where the database is located. The default value is `localhost`.
* `DB_PORT` is the port on which the database is running. The default value is `5432`.
* `DB_NAME` is the name of the database that is used to store the data. The default value is `stackexchange`. It should
  have the same value as the one you used when creating the database.
* `DB_USER` is the name of the PostgreSQL user that will be used to access the database. This should be set to the value
  of the username you created.
* `DB_PASSWORD` is the password of the PostgreSQL user that will be used to access the database.  This should be set to
  value of the password that you have set when creating the user.

## Loading data

First, you must load the available stackexchange sites by running the command:

```
$ uv run manage.py load_sites
```

Then you can load data for a specific site to the database by running the `loaddata` Django command. For example, in
order to load the data for the `superuser.com` site, run the following command:

```
$ uv run manage.py load_data superuser
```

## Running the application

Now everything should be ready to launch the application by running:

```
$ uv run manage.py runserver
```

The application should now be available at http://127.0.0.1:8000. The API documentation is built with
[Swagger](https://swagger.io/), and you can access it by opening http://127.0.0.1:8000/api/doc. It documents all the
endpoints that you can use in order to access the data.

You can also access the Django admin interface at http://127.0.0.1:8000/admin. The credentials to access the interface
are admin/password.

### Development

In order to run the application tests, run

```shell
uv run manage.py test
```

To get an HTML coverage report, run

```shell
uv run coverage run manage.py test --no-input
uv run coverage html
```

The report will be available in the `htmlcov` directory.

In order to get a linting report with [Pylint](https://www.pylint.org/), run

```shell
uv run pylint stackexchange
```

In order to get a security report with [Bandit](https://bandit.readthedocs.io), run

```shell
uv run bandit -r .
```

In order to get a vulnerability report for the project dependencies with
[Safety](https://safetycli.com/product/safety-cli), run

```shell
uv run safety scan
```