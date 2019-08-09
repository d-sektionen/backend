from .models import Item, Booking
from django.contrib.auth.models import User
from rest_framework import serializers
from account.serializers import SimpleUserSerializer
from datetime import timedelta

class ItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = Item
    fields = ('id', 'name', 'description')
    read_only_fields = ('id', 'name', 'description')

class BookingSerializer(serializers.ModelSerializer):
  user = SimpleUserSerializer(read_only=True)
  user_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all(), source="user", default=serializers.CurrentUserDefault())
  item_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Item.objects.all(), source="item")
  item = ItemSerializer(read_only=True)

  class Meta:
    model = Booking
    fields = ('id', 'start', 'end', 'user', 'user_id', 'item_id', 'item', 'description')

  def validate(self, attrs):
    # Start should be before end
    if attrs['start'] > attrs['end']:
      raise serializers.ValidationError('Booking should start before it ends.')
    # Check lowest duration
    if attrs['start'] + timedelta(minutes=30) > attrs['end']:
      raise serializers.ValidationError('Booking should be at least 30 minutes.')
    # Check longest duration
    if attrs['start'] + timedelta(days=7) < attrs['end']:
      raise serializers.ValidationError('Booking should be at most 7 days.')

    # Check overlap
    overlap_query = Booking.objects.filter(item=attrs['item'])
    if (self.instance):
      overlap_query = overlap_query.exclude(pk=self.instance.id)
    overlap_query = overlap_query.filter(start__lte=attrs['end'], end__gte=attrs['start'])
    if overlap_query.exists():
      raise serializers.ValidationError('Booking overlaps with another booking.')
    return attrs