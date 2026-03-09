from django.apps import AppConfig


class VotingConfig(AppConfig):
    name = "backend.voting"

    def ready(self):
        import backend.voting.signals

    # def ready(self):
    #     import voting.sockets
