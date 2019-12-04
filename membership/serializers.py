from rest_framework import serializers

# from rest_framework.validators import UniqueValidator
# from django.contrib.auth.models import User

from .models import Request


class RequestSerializer(serializers.ModelSerializer):

    username = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        # validators=[UniqueValidator(queryset=User.objects.all())],
    )

    infomail_subscriber = serializers.BooleanField(default=False, required=False, write_only=True)

    class Meta:
        model = Request
        fields = (
            "username",
            "first_name",
            "last_name",
            "program",
            "starting_year",
            "message",
            "infomail_subscriber",
        )

    def create(self, validated_data):
        user = self.context['request'].user
        user.profile.infomail_subscriber = validated_data.pop('infomail_subscriber')
        user.profile.save()
        return super().create(validated_data)
            

        read_only_fields = ("username",)
        
