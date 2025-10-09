"""
In this file you can add cronjobs and timers using uwsgi decorators, see:
https://uwsgi-docs.readthedocs.io/en/latest/PythonDecorators.html
"""

from django.core import management

from uwsgidecorators import cron
from datetime import datetime


@cron(10, 3, -1, -1, -1)
def nightly(num):
    print(f"Running nightly command. {datetime.now()}")
    management.call_command("nightly")
