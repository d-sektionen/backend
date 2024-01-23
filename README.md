# D-sektionens API (Django)

Work in progress to create a common API in Django.

## Note about wagtail-integration branch

Work is being done to migrate all backends (Wordpress, advent calendar, etc.) into a single app.
All of these will be migrated to this repository and when finished this repository should probably be renamed to `backend`.

The goal of this is to have a well structured, well connected backend at `backend.d-sektionen.se` where different front end applications can fetch data.
The backend should therefore contain mostly api based (for example, REST or GraphQL) products.
A guideline is that **a normal visitor should not see `backend.d-sektionen.se` in their url bar.** Although it would be accepted for a content editor to see it.

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

Every time you make a modification to the database structure, run this:

```sh
./manage.py migrate
```

Note: You will need to run the migration command if you encounter the
following error message:

```sh
You have 13 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
```

Start the Django development server and begin developing:

```sh
./manage.py runserver
```

If you're using MAC OS, check out: https://stackoverflow.com/a/53310545/9966843

## Accessing content

For now, the only way to access content is to visit the Django admin
site. This can be found at http://127.0.0.1:8000/admin.

If you are denied access to anything, try running the following in your terminal:
```sh
./manage.py add_super_user <username>
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
