from django.apps import AppConfig


class VotingConfig(AppConfig):
    name = "backend.voting"

    def ready(self):
        import backend.voting.signals  # noqa: F401
