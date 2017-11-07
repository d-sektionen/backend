# D-sektionens API (Django)
Work in progress to create a common API in Django. 

## Setting up a local development environment
Create a virtualenv with a Python 3 interpreter and activate it:
```sh
# Install virtualenv if not already installed
pip install virtualenv

# Setup and activate virtualenv
virtualenv -p python3 .venv
source .venv/bin/activate
```

**Note: All the following commands assume that you have activated the 
virtual environment using `source .venv/bin/activate` in your terminal.**

Then install the needed Python dependencies:
```sh
pip install -r requirements.txt
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

## Accessing content
For now, the only way to access content is to visit the Django admin
site. This can be found at http://127.0.0.1:8000/admin.
