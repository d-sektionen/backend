from rest_framework import serializers

# from rest_framework.validators import UniqueValidator
# from django.contrib.auth.models import User

from .models import Request


class RequestSerializer(serializers.ModelSerializer):

    username = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        # validators=[UniqueValidator(queryset=User.objects.all())],
    )

    class Meta:
        model = Request
        fields = (
            "username",
            "first_name",
            "last_name",
            "program",
            "starting_year",
            "message",
        )
        read_only_fields = ("username",)
