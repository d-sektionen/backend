from rest_framework import serializers
from account.serializers import SimpleUserSerializer
from .models import Event, Doorkeeper

class RegisterSerializer(serializers.Serializer):
  event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
  identifier = serializers.CharField(max_length=200)
  identifier_type = serializers.ChoiceField([
    ('AU', 'Automatic'),
    ('UN', 'Username'),
    ('CI', 'Card ID'),
  ], default="AU")
  action = serializers.CharField(max_length=24)

class EventSerializer(serializers.ModelSerializer):
  actions = serializers.SerializerMethodField()

  def get_actions(self, obj):
    return obj.ACTIONS

  class Meta:
    model = Event
    fields = ('id', 'name', 'archived', 'actions')
    read_only_fields = ('id', 'name', 'archived', 'actions')

class DoorkeeperSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    user = SimpleUserSerializer(read_only=True)
    event_id = serializers.IntegerField(write_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Doorkeeper
        fields = ('id', 'user_id', 'user', 'event_id', 'event')
