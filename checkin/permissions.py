from rest_framework.permissions import BasePermission
from django.contrib.contenttypes.models import ContentType
from .models import EventBase, Doorkeeper

class OnlyDoorkeepersRegister(BasePermission):
    def has_permission(self, request, view):
      # Non POST actions are not allowed but should not return a 403.
      # This makes sure they can return the 405
      if  request.method != 'POST':
        return True

      if request.user:
        try:
          event = EventBase.objects.get(pk=request.data['event'])
        except:
          return False
        return Doorkeeper.objects.filter(user=request.user, event=event).exists()
      else:
        return False

class DoorkeeperPermission(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_permission(self, request, view):
        # return True
        event_id = request.data.get("event_id")
        if event_id is None:
            event_id = request.query_params.get("event_id")
        
        if event_id is None:
          return request.user.has_perm('checkin.view_doorkeeper') if request.method == 'GET' else True
        
        try:
          event = EventBase.objects.get_subclass(pk=event_id)
        except EventBase.DoesNotExist:
          return True

        # Create permission string for subclass of event
        # It will check if a user has permission to manipulate the EventBase type instead of a Doorkeeper.
        # Which is not entirely correct but should be fine.
        event_meta = ContentType.objects.get_for_model(event)
        event_permission = lambda t: event_meta.app_label + '.' + t + '_' + event_meta.model

        if request.method == "GET":
            return request.user.has_perms(['checkin.view_doorkeeper', event_permission('view')])
        if request.method == "POST":
            return request.user.has_perms(['checkin.add_doorkeeper', event_permission('add')])

        return True

    def has_object_permission(self, request, view, obj):
        event = EventBase.objects.get_subclass(pk=obj.event.id)

        # Create permission string for subclass of event
        # It will check if a user has permission to manipulate the EventBase type instead of a Doorkeeper.
        # Which is not entirely correct but should be fine.
        event_meta = ContentType.objects.get_for_model(event)
        event_permission = lambda t: event_meta.app_label + '.' + t + '_' + event_meta.model

        if request.method == "GET":
            return request.user.has_perms(['checkin.view_doorkeeper', event_permission('view')])
        if request.method == "DELETE":
            return request.user.has_perms(['checkin.delete_doorkeeper', event_permission('delete')])


        return True