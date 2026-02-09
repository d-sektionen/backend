"""
WSGI config for dsek project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

try:
    import uwsgidecorators
    from django.core.management import call_command

    @uwsgidecorators.timer(100)
    def send_queued_mail(num):
        """Send queued mail every 10 seconds"""
        call_command("send_queued_mail", processes=1)

except ImportError:
    print("uwsgidecorators not found. Cron and timers are disabled")
