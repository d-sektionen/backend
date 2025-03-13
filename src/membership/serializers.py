from rest_framework import serializers

from .models import Request


class RequestSerializer(serializers.ModelSerializer):
    username = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    infomail_subscriber = serializers.BooleanField(
        default=False, required=False, write_only=True
    )

    liu_card_id = serializers.CharField(required=False, max_length=17, write_only=True)

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
            "liu_card_id",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        user.profile.infomail_subscriber = validated_data.pop("infomail_subscriber")

        if validated_data.get("liu_card_id"):
            user.profile.liu_card_id = validated_data.pop("liu_card_id")

        user.profile.save()
        print(validated_data)

        return super().create(validated_data)
