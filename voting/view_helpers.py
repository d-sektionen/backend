from rest_framework import mixins, viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from app.decorators import extract_user, extract_username, extract_data
from voting.models import Meeting


def different_read_serializer(cls):
    class DifferentReadSerializer(cls):

        def __init__(self, *args, **kargs):
            super(DifferentReadSerializer, self).__init__(*args, **kargs)

        def get_serializer_class(self):
            if self.request.method == 'GET':
                return self.read_serializer_class

            # The read serializer does not support foreign keys in requests properly,
            # so return the normal serializer.
            return self.serializer_class

    return DifferentReadSerializer


class UserIdentifiableViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    check_section_membership = False

    def get_model(self):
        return self.serializer_class.Meta.model

    @extract_user
    def create(self, request, *args, **kwargs):
        meeting_id = extract_data(request, 'meeting')
        meeting = Meeting.objects.get(id=meeting_id)
        user = kwargs['user']

        # Verify that the user is a member of the section if configured to do so
        if self.check_section_membership and not meeting.section.is_member(user):
            return Response({'error': self.get_model().get_model_name() + ' måste tillhöra sektionen'}, status=status.HTTP_400_BAD_REQUEST)

        attendant, created = self.get_model().objects.get_or_create(user=user, meeting=meeting)

        if created:
            return Response(self.serializer_class(attendant).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': self.get_model().get_model_name() + ' redan registrerad'}, status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['delete'], url_path='')
    @extract_username
    def delete(self, request, *args, **kwargs):
        meeting_id = extract_data(request, 'meeting')
        meeting = Meeting.objects.get(id=meeting_id)
        username = kwargs['username']

        attendant = self.get_model().objects.filter(user__username=username, meeting=meeting).first()
        if attendant is not None:
            attendant.delete()
            return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': self.get_model().get_model_name() + ' inte registrerad på mötet'}, status=status.HTTP_400_BAD_REQUEST)
