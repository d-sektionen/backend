from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins, viewsets, status
from django.contrib.auth.models import User

from account.models import Profile
from . import serializers
from .models import Event

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Events where the user is a doorkeeper items to be viewed.
    """
    queryset = Event.objects.all().select_subclasses()
    serializer_class = serializers.EventSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        queryset = queryset.filter(doorkeeper__user__pk = user.pk).filter(archived = False)
        return queryset

class RegisterViewSet(viewsets.ViewSet):
  """
  Viewset with only POST for Doorkeepers to do an action for people to an Event.
  """
  serializer_class = serializers.RegisterSerializer

  def create(self, request):
    serializer = serializers.RegisterSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(
        {
          'detail': 'Validation of fields "' + ', '.join(serializer.errors.keys()) + '" failed.',
          'errors': serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
      )

    identifier = serializer.data['identifier']
    identifier_type = serializer.data['identifier_type']
    

    if (identifier_type == 'AU'):
      # Checks if card id by checking if identifier is numeric, else it's a username. Could be improved.
      identifier_type = 'CI' if identifier.isnumeric() else 'UN'

    user = None
    try:
      if (identifier_type == 'CI'):
        user = Profile.objects.get(liu_card_id=identifier).user
      elif (identifier_type == 'UN'):
        user = User.objects.get(username__iexact=identifier)
    except:
      return Response({ 'detail': 'User not found.' }, status=status.HTTP_400_BAD_REQUEST)

    action = serializer.data['action']
    event = Event.objects.get_subclass(pk=serializer.data['event'])

    return event.on_register(user, action) # Response(event.name, status=status.HTTP_200_OK)