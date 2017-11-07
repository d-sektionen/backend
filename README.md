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

Then install the needed Python dependencies:
```sh
pip install -r requirements.txt
```

Every time you make a modification to the database structure, run this:
```sh
./manage.py migrate
```

Start the Django development server and begin developing:
```sh
./manage.py runserver
```
