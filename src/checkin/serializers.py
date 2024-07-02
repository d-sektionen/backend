from rest_framework import serializers
from django.contrib.auth.models import User

from account.serializers import SimpleUserSerializer
from account.models import Profile
from account.idtoken import read_id_token

from .models import EventBase, Doorkeeper

IDTYPE_AUTO = "auto"
IDTYPE_CARD_ID = "card_id"
IDTYPE_ID_TOKEN = "id_token"
IDTYPE_USERNAME = "username"


class UserIdentifierField(serializers.Field):
    def __init__(self, **kwargs):
        kwargs["write_only"] = True
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        idtypes = [IDTYPE_AUTO, IDTYPE_CARD_ID, IDTYPE_ID_TOKEN, IDTYPE_USERNAME]

        if not data:
            return None

        if not isinstance(data, str):
            msg = "Incorrect type. Expected a string, but got %s"
            raise serializers.ValidationError(msg % type(data).__name__)
        try:
            identifier_type, identifier = data.split(":", 1)
        except (ValueError):
            raise serializers.ValidationError(
                f"Incorrect format. Expected `TYPE:VALUE`. Where TYPE is one of {', '.join(idtypes)}."
            )

        if identifier_type not in idtypes:
            raise serializers.ValidationError(
                f"Incorrect format. Expected `TYPE:VALUE`. Where TYPE is one of {', '.join(idtypes)}."
            )

        if identifier_type == IDTYPE_AUTO:
            if identifier.isnumeric():
                # Checks if card id by checking if identifier is numeric. Could be improved.
                identifier_type = IDTYPE_CARD_ID
            elif "," in identifier:
                # Checks if idtoken by checking if identifier is long, also a bad solution since usernames can be up to 150 chars.
                identifier_type = IDTYPE_ID_TOKEN
            else:
                # else it's a username.
                identifier_type = IDTYPE_USERNAME

        user = None
        try:
            if identifier_type == IDTYPE_CARD_ID:
                user = Profile.objects.get(liu_card_id=identifier).user
            elif identifier_type == IDTYPE_USERNAME:
                user = User.objects.get(username__iexact=identifier)
            elif identifier_type == IDTYPE_ID_TOKEN:
                user = read_id_token(identifier)
        except:
            pass  # if exception we return none user (could be more specific)

        return user


class RegisterSerializer(serializers.Serializer):
    event = serializers.PrimaryKeyRelatedField(queryset=EventBase.objects.all())
    user = UserIdentifierField()
    # identifier = serializers.CharField(max_length=200)
    # identifier_type = serializers.ChoiceField(
    #     [("AU", "Automatic"), ("UN", "Username"), ("CI", "Card ID"),], default="AU"
    # )
    action = serializers.CharField(max_length=24)


class EventBaseSerializer(serializers.ModelSerializer):
    actions = serializers.SerializerMethodField()
    status_message = serializers.SerializerMethodField()

    def get_status_message(self, obj):
        return obj.get_status_message()

    def get_actions(self, obj):
        return obj.ACTIONS

    class Meta:
        model = EventBase
        fields = ("id", "name", "archived", "actions", "status_message")
        read_only_fields = ("id", "name", "archived", "actions", "status_message")


class DoorkeeperSerializer(serializers.ModelSerializer):
    user_username = serializers.SlugRelatedField(
        slug_field="username",
        write_only=True,
        queryset=User.objects.all(),
        source="user",
    )
    user = SimpleUserSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=EventBase.objects.all(), source="event"
    )
    event = EventBaseSerializer(read_only=True)

    class Meta:
        model = Doorkeeper
        fields = ("id", "user_username", "user", "event_id", "event")
