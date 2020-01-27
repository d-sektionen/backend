from rest_framework import serializers
from django.contrib.auth.models import User

from account.serializers import SimpleUserSerializer

from .models import EventBase, Doorkeeper

class RegisterSerializer(serializers.Serializer):
  event = serializers.PrimaryKeyRelatedField(queryset=EventBase.objects.all())
  identifier = serializers.CharField(max_length=200)
  identifier_type = serializers.ChoiceField([
    ('AU', 'Automatic'),
    ('UN', 'Username'),
    ('CI', 'Card ID'),
  ], default="AU")
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
    fields = ('id', 'name', 'archived', 'actions', 'status_message')
    read_only_fields = ('id', 'name', 'archived', 'actions', 'status_message')

class DoorkeeperSerializer(serializers.ModelSerializer):
    user_username = serializers.SlugRelatedField(slug_field='username', write_only=True, queryset=User.objects.all(), source="user")
    user = SimpleUserSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=EventBase.objects.all(), source='event')
    event = EventBaseSerializer(read_only=True)

    class Meta:
        model = Doorkeeper
        fields = ('id', 'user_username', 'user', 'event_id', 'event')
