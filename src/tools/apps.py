"""
Tools is an app which contains very small applications that don't need their own app.

For example a rest framework endpoint which converts the d-sektionen calendar to an easy to use json endpoint and the netlight door lock.
"""

from django.apps import AppConfig


class ToolsConfig(AppConfig):
    name = "tools"
