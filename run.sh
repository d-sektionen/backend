#!/bin/bash

cd /srv/api/website
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=app.settings_production
daphne -b 127.0.0.1 -p 8080 app.asgi:channel_layer &
echo $! > run.1.pid
python manage.py runworker &
echo $! > run.2.pid
wait `cat run.1.pid` `cat run.2.pid`
