# StackExchange Django

This project implements an API for a [StackExchange](https://stackexchange.com/)-like site. The API tries to be as
faithful as possible to the [official stackexchange API](https://api.stackexchange.com/docs). Data for the application
can be loaded with the data dump available at [archive.org](https://archive.org/details/stackexchange). Those dumps
used to be updated regularly, but it seems that since April 2024, no new dumps are uploaded.

The application is built with [Django](https://www.djangoproject.com/), using [Python](https://www.python.org) and
[Poetry](https://python-poetry.org/) for dependency management. [PostgreSQL](https://www.postgresql.org/) is used as the
project database. [Redis](https://redis.io/) is used as a broker for background application tasks and as the caching
backend.

## Installation

Before running these installation instructions, make sure you have [Python](https://www.python.org/downloads/),
[Poetry](https://python-poetry.org/docs/#installation), [PostgreSQL](https://www.postgresql.org/download/), and
[Redis](https://redis.io/) installed.

```
$ poetry install
```

Then, you can activate the Python virtual environment by running:

```
$ poetry shell
```

All commands from this point forward require that the virtual environment is activated.

### Database

Before running the application, you need to create the database where the data will be stored, and the database user
that will be used to access the data. You can do this by running:

```
$ sudo -u postgres psql

postgres=# create database stackexchange;
postgres=# create user stackexchange with encrypted password 'stackexchange' createdb;
```

You can change the database name, user and password to whatever values you wish.

### Environment values

Another prerequisite before running the application is to create an `.env` file in the project directory that will hold
the environment variables that will configure the application. A sample file that you can use as a template exists in
the root directory of the application and is named `.env.example`. The environment variables that can be set are:

* `SECRET_KEY` is the value of the [Django secret key](https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-SECRET_KEY).
  The key is used to provide cryptographic signing, and should be set to a unique, unpredictable value. You can generate
  one by running `python -c 'from django.core.management.utils import get_random_secret_key;print(get_random_secret_key())'`
* `DB_HOST` is the name of the host where the database is located. The default value is `localhost`.
* `DB_PORT` is the port on which the database is running. The default value is `5432`.
* `DB_NAME` is the name of the database that is used to store the data. The default value is `stackexchange`. It should
  have the same value as the one you used when creating the database.
* `DB_USER` is the name of the PostgreSQL user that will be used to access the database. This should be set to the value
  of the username you created.
* `DB_PASSWORD` is the password of the PostgreSQL user that will be used to access the database.  This should be set to
  value of the password that you have set when creating the user.

### Loading data

First, you must load the available stackexchange sites by running the command:

```
$ python manage.py loadsites
```

Then you can load data for a specific site to the database by running the `loaddata` Django command. For example, in
order to load the data for the `superuser.com` site, run the following command:

```
$ python manage.py loaddata superuser
```

### Running the application

Now everything should be ready to launch the application by running:

```
$ python manage.py runserver
```

The application should now be available at http://127.0.0.1:8000. The API documentation is built with
[Swagger](https://swagger.io/), and you can access it by opening http://127.0.0.1:8000/api/doc. It documents all the
endpoints that you can use in order to access the data.

You can also access the Django admin interface at http://127.0.0.1:8000/admin. The credentials to access the interface
are admin/password.

### Development

In order to run the application tests, run

```shell
python manage.py test
```

To get an HTML coverage report, run

```shell
coverage run manage.py test --no-input
coverage html
```

The report will be available in the `htmlcov` directory.

In order to get a linting report with [Pylint](https://www.pylint.org/), run

```shell
pylint stackexchange
```

In order to get a security report with [Bandit](https://bandit.readthedocs.io), run

```shell
bandit -r .
```

In order to get a vulnerability report for the project dependencies with
[Safety](https://safetycli.com/product/safety-cli), run

```shell
safety scan
```