from rest_framework import serializers
from django.contrib.auth.models import User

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
    user_username = serializers.SlugRelatedField(slug_field='username', write_only=True, queryset=User.objects.all(), source="user")
    user = SimpleUserSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Event.objects.all(), source='event')
    event = EventSerializer(read_only=True)

    class Meta:
        model = Doorkeeper
        fields = ('id', 'user_username', 'user', 'event_id', 'event')
