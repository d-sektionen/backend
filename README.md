# D-sektionens API (Django) 

This project provides an API for communicating with D-sektionens main server. This API is used by most of D-sektionens other projects.

## Setting up a local development environment

### Requirements

* Docker
* Python 3.9 or later.

### Disclaimers

**Note**: All of the following is done in git branch `development`. Switch to it using `git switch development` if necessary.

**Note**: This project expects familiarity with Python, Django and Django REST-framework.

**Note**: While it is possible to run the development server without using Docker, this is not advised.

### 1. Pre-commit hooks

**Optional but recommended:** Install pre-commit hooks using (linting, formatting, etc):

```sh
pre-commit install
```

### 2. Environment variables

Certain environment variables must be set before running the project:

Rename `.env.sample` to `.env`:

```sh
mv .env.sample .env
```

..and open `.env` in a text editor.

The following environment variable must be set (the rest should or can be left blank):

**Important: ask someone on the dev team for the current `CLIENT_ID` value.**

```sh
# ADFS Client ID.
CLIENT_ID=
```

**Note**: At the moment there is no point in setting `SUPERUSER_USERNAME` or `SUPERUSER_EMAIL` fields since Django admin pages require a password (which the current Dockerfile does not set). This will have to be done manually in a later step.

### 3. Docker

Set up Docker with:

```sh
docker compose up
```

In the future, use this command to start the local development server.

**Note**: If you are using MacOS, check out: <https://stackoverflow.com/a/53310545/9966843>

The server should now be up and running at <http://127.0.0.1:8000>. This url should give a 404-error and a list of available routes if everything is working. If not, something has gone wrong during previous steps.

When setup is complete, open a new terminal and follow the steps in the following sections.

### 4. Making migrations

When the database is modified (or during setup) run the following command:

```sh
docker compose exec backend python manage.py migrate
```

This will migrate your tables (models) to the database or create the database if it doesn't exist.

**Note**: Whenever changes are made to any of your models, you will need to run the migration command. The same applies if you encounter the following error message:

```sh
You have 13 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
```

### 5. Accessing content

To manage the database (manage users, approve requests, create meetings etc.) you need an admin account:

```sh
docker compose exec backend python manage.py createsuperuser
```

You will be prompted for additional information. Everything can be left blank except for the password. The default username should be `root`.

To login and access the admin panel visit <http://127.0.0.1:8000/admin>.

### 6. Frontend

If you want a working frontend, see <https://github.com/d-sektionen/medlem> and follow README.md to get started. Having a working frontend is necessary if you want to test how the backend interacts with the user interface presented to ordinary members of D-sektionen.

# Technologies used in this project

The following is a list of technologies (including modules and libraries) used in this project:

*TODO*

# Additional resources

You can learn more about the technologies used in this project at: 

* [docs.djangoproject.com](https://docs.djangoproject.com)
* [www.django-rest-framework.org](https://www.django-rest-framework.org)
* [docs.docker.com](https://docs.docker.com)
