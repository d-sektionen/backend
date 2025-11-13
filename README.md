# D-sektionens API (Django)

## Requirements

* Python 3.9 or later.
* Familiarity with Python, Django and Django REST-framework

## Setting up a local development environment

**Note**: All of the following is done in git branch 'development'. Switch to it using `git switch development` if necessary.

**Note**: Depending on your system, the Python command may be `python3`, `python`, or `py`.
Use whichever command runs Python 3 on your machine.

### Create a virtual environment

#### Linux/Mac

Navigate to the projects root directory and create a new virtual environment with:

```sh
python3 -m venv .venv
```

**Note**: The rest of the guide will assume that you have activated the
virtual environment using `source .venv/bin/activate` in your terminal.

#### Windows

Open Powershell as Administrator

```
set-executionpolicy remotesigned
```

In repository root folder:

```sh
python -m venv .venv
.venv/Scripts/activate
```

**Note**: The rest of the guide will assume that you have activated the
virtual environment using `.venv/Scripts/activate` in your terminal.

### Install Python dependencies

```sh
pip3 install -r requirements.development.txt
```

### Pre-commit hooks

**Optional but recommended:** Install pre-commit hooks using (linting, formatting, etc):

```sh
pre-commit install
```

### Environment variables

Certain environment variables must be set before running the project:

Rename `.env.sample` to `.env`:

```sh
mv .env.sample .env
```

..and open `.env` in a text editor.

The following environment variable must be set: (the rest should or can be left blank):

**Important: ask someone on the dev team for the current `CLIENT_ID` value.**

```sh
# ADFS Client ID.
CLIENT_ID=
```

### Docker

Set up Docker with:

```sh
docker compose up
```

When setup is complete, close the server

**Note:** If you are not using Docker to run your local server, export the environment variable `CLIENT_ID` manually (**WARNING: Not running the server via Docker sacrifices some functionality like the lock API.**):

```sh
export CLIENT_ID=[VALUE]
```

### Making migrations

When the database is modified, or on first run, run the following command:

```sh
python3 manage.py migrate
```

This will migrate your tables (models) to the database or create the database if it doesn't exist.

**Note: You will need to run the migration command if you encounter the
following error message:**

```sh
You have 13 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
```

### Start the server

If you are using MacOS, check out: <https://stackoverflow.com/a/53310545/9966843>

Start the Django development server and begin developing:

With Docker:

```sh
docker compose up
```

Without:

```sh
python3 manage.py runserver
```

The server should now be up and running at <http://127.0.0.1:8000>. This url should give a 404-error and a list of available routes if everything is working. If not, something has gone wrong during previous steps.

## Accessing content

To manage the database (manage users, approve requests, create meetings etc.) you need an admin account:

```sh
python3 manage.py createsuperuser
```

You will be prompted for additional information. Everything can be left blank except for password

To login and access the admin panel visit <http://127.0.0.1:8000/admin>.

## Frontend

If you want a working frontend, see <https://github.com/d-sektionen/medlem> and follow the README.md to get started. Having a working frontend is necessary if you want to test how the backend interacts with the user interface presented to ordinary members of d-sektionen.

<!-- WIP proposed section to expand or delete, depending on opinion -->

# Additional resources

You can learn more about the technologies used in this project at: 

* <docs.djangoproject.com>
* <www.django-rest-framework.org/>
* <docs.docker.com/>