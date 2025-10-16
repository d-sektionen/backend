# D-sektionens API (Django)

## Setting up a local development environment

Create a virtualenv with a Python 3 interpreter and activate it:

Should be at least python version 3.7.

Setup and activate virtualenv

### Linux/Mac

```sh
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

Open Powershell as Administer

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
pip install -r development.txt
```

**Optional but recommended:** Install pre-commit hooks using (linting, formatting, etc):

```
pre-commit install
```

### Starting the server using Docker
As of Oct 13, 2025 this project uses Docker's compose feature to run its development server. After populating the `.env` file, simply run:
```sh
> docker compose up
```

When starting the server for the first time, or after changes have been made in the database, the database must be migrated. You can do this easily by using docker's `exec` command while the server is running.
```sh
> docker compose exec backend python manage.py migrate
```


If you're using MAC OS, check out: <https://stackoverflow.com/a/53310545/9966843>

## Accessing content

For now, the only way to access content is to visit the Django admin
site. This can be found at <http://127.0.0.1:8000/admin>.

If you are denied access to anything, try running the following in your terminal:

```sh
./manage.py add_super_user <username>
```

## Email

Email needs to be configured through the .env file.

```bash
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

# Documentation

## uwsgitop

If you want to run something like "top" but for uwsgi.
Go into the .venv in the backend-project and run:

```sh
uwsgitop http://127.0.0.1:1235
```

## Account

### GET /account/token

Redirects the user to the LiU login page and upon successful login returns a json object containing a token. Example:

```
{
    "token": "YOUR TOKEN HERE"
}
```

### GET /account/token?redirect=URL

Same as the normal token endpoint but instead of returning a json object redirects the user to the supplied URL with an added query parameter (`URL?token=YOURTOKENHERE`).

### GET /account/user/ID

Retrieves a user. The ID can be a numerical identifier (as stored in the database), or the string "me" for the currently logged in user. Example:

```
{
    {
        "username": "patsl736",
        "first_name": "Patrik",
        "last_name": "Sletmo",
        "groups": [
            {
                "name": "D-sektionen"
            },
            {
                "name": "Admins for D-sektionen"
            },
            {
                "name": "Admins for I-sektionen"
            }
        ],
        "sections": [
            {
                "id": 1,
                "name": "D-sektionen"
            },
            {
                "id": 2,
                "name": "I-sektionen"
            }
        ]
    }
}
```
