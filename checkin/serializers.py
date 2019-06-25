from rest_framework import serializers
from .models import Event

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