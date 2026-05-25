# D-sektionens API (Django) 

This project provides an API for communicating with D-sektionens main server. This API is used by most of D-sektionens other projects.

## Requirements

Should be at least Python version 3.12 since [PEP 695 – Type Parameter Syntax](https://peps.python.org/pep-0695/) is used

To check your installed Python version

```sh
python3 --version
```

## Disclaimers

**Note**: This project expects familiarity with Python, Django and Django REST-framework.

**Note**: While it is possible to run the development server without using Docker, this is not advised. Further down are instructions on how to set it up locally without docker.

### 1. Environment variables

Certain environment variables must be set before running the project:

Rename and/or copy `.env.sample` to `.env`:

```sh
mv .env.sample .env
```

..and open `.env` in a text editor.

The following environment variable must be set:
```sh
CLIENT_ID=
CLIENT_SECRET=
LIU_TENANT_ID=
```
These values are secret and are given to you by your webmaster/someone on the dev team.

**Note**: At the moment there is no point in setting `SUPERUSER_USERNAME` or `SUPERUSER_EMAIL` fields since Django admin pages require a password (which the current Dockerfile does not set). This will have to be done manually in a later step.

### 2. Starting the server using Docker
As of October 2025, this project uses Docker Compose. After populating your .env file, start the server and run migrations with:

```sh
docker compose up
```

**Note**: If you are using MacOS, check out: <https://stackoverflow.com/a/53310545/9966843>

The server should now be up and running at <http://127.0.0.1:8000>. This url should give a 404-error and a list of available routes if everything is working. If not, something has gone wrong during previous steps.

When setup is complete, open a new terminal and follow the steps in the following sections.

### 3. Making migrations

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

### 4. Accessing content

To manage the database (manage users, approve requests, create meetings etc.) you need an admin account:

```sh
docker compose exec backend python manage.py createsuperuser
```

You will be prompted for additional information. Everything can be left blank except for the password. The default username should be `root`.

To login and access the admin panel visit <http://127.0.0.1:8000/admin>.

### 5. Frontend

If you want a working frontend, see <https://github.com/d-sektionen/medlem> and follow README.md to get started. Having a working frontend is necessary if you want to test how the backend interacts with the user interface presented to ordinary members of D-sektionen.

## Setting up a local development environment (Without docker)

### Setup and activate the virtual environment

### Linux/Mac

```sh
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

Open Powershell as Administer. This only needs to be run once per computer.

```
set-executionpolicy remotesigned
```

In repository root folder

```
python -m venv .venv
.venv/Scripts/activate
```

**Note: All the following commands assume that you have activated the
virtual environment using `source .venv/bin/activate` in your terminal.**

Then install the needed Python dependencies:

```sh
pip install -r requirements.development.txt
```

**Optional but recommended:** Install pre-commit hooks using (linting, formatting, etc):

```
pre-commit install
```

### Making migrations
Running the following command is necessary the first time you start the server and everytime you make changes to the database.
```
python manage.py migrate
```

### Creating a super user
In order to access the admin page at http://127.0.0.1:8000/admin, you'll need to create a super user.

```
python manage.py createsuperuser
```

### Starting the server
Once all the setup is completed, you can run the server with the following command.
```
python manage.py runserver
```

For the frontend, see <https://github.com/d-sektionen/medlem>.


# Technologies used in this project

The following is a list of technologies (including modules and libraries) used in this project:

*TODO*

# Additional resources

You can learn more about the technologies used in this project at: 

* [docs.djangoproject.com](https://docs.djangoproject.com)
* [www.django-rest-framework.org](https://www.django-rest-framework.org)
* [docs.docker.com](https://docs.docker.com)
