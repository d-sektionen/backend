from .models import Item, Booking
from django.contrib.auth.models import User
from rest_framework import serializers
from account.serializers import SimpleUserSerializer

class ItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = Item
    fields = ('id', 'name', 'description')
    read_only_fields = ('id', 'name', 'description')

class BookingSerializer(serializers.ModelSerializer):
  user = SimpleUserSerializer(read_only=True, default=serializers.CurrentUserDefault())
  #user = serializers.HyperlinkedRelatedField(queryset=User.objects.all(), view_name="user-detail")
  item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())
  item_obj = ItemSerializer(read_only=True, source="item")

  class Meta:
    model = Booking
    fields = ('id', 'start', 'end', 'user', 'item_obj' , 'item', 'description')

  def validate(self, attrs):
    instance = Booking(**attrs)
    instance.clean()
    return attrs