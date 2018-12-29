from django.apps import AppConfig

"""
Tools is an app which contains very small applications that don't need their own app.

For example a rest framework endpoint which converts the d-sektionen calendar to an easy to use json endpoint.
"""
class ToolsConfig(AppConfig):
    name = 'tools'
