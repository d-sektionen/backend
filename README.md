# D-sektionens API (Django)


## Setting up a local development environment
The project requires at least Python version 3.9.
### Create a virtualenv with a Python 3 interpreter and activate it:

Setup and activate virtualenv:

#### Linux/Mac
```sh
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows
Open Powershell as Administrator 
```
set-executionpolicy remotesigned
```

In repository root folder:
```
python -m venv .venv
.venv/Scripts/activate
```

**Note: All the following commands assume that you have activated the
virtual environment using `source .venv/bin/activate` in your terminal.**

#### Install the needed Python dependencies:

```sh
pip install -r development.txt
```

Every time you make a modification to the database structure, run this:

```sh
./manage.py migrate
```

**Note: You will need to run the migration command if you encounter the
following error message:**

```sh
You have 13 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
```

Start the Django development server and begin developing:

```sh
./manage.py runserver
```

If you're using MAC OS, check out: https://stackoverflow.com/a/53310545/9966843

## Environment variables
The project requires some environment variables to be set. The following is a sample of what an `.env` file may look like.
```bash
CLIENT_ID=
```
The following variables are optional:
```bash
YALE_EMAIL=
YALE_PASSWORD=
BETTAN_LOCK_ID=
CONFIGURA_LOCK_ID=
WERK_WEBHOOK_URL=
```
Keep in mind some functionality may not work without the optional variables.

## Accessing content

The only way to access content is to visit the Django admin
site. This can be found at http://127.0.0.1:8000/admin.

To be able to log in to the admin site, you first need to visit http://127.0.0.1:8000/account/admin_device_login.
Once there, authenticate using your LiU details. Then you can return to the admin site.

If you are denied access to anything, try running the following in your terminal:
```sh
./manage.py add_super_user <username>
```
Unlike `manage.py createsuperuser`, this will upgrade the account to superuser if it already exists.
