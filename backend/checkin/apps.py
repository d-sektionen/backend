from django.apps import AppConfig


class CheckinConfig(AppConfig):
    name = "backend.checkin"

    def ready(self):
        import backend.checkin.signals  # noqa: F401
