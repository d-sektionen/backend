from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response

from account import kobra


def extract_user(func):
    @extract_username
    def extract_user_impl(self, request, *args, **kwargs):
        username = kwargs['username']
        user, created = User.objects.get_or_create(username=username)
        return func(self, request, user=user, *args, **kwargs)

    return extract_user_impl


def extract_username(func):
    def extract_username_impl(self, request, *args, **kwargs):
        if 'card_id' in request.data:
            card_id = request.data['card_id']
            username = kobra.liu_id_from_card(card_id)
        elif 'username' in request.data:
            username = request.data['username'].strip().lower()
        else:
            return Response({'error': 'Missing required parameter username or card_id'}, status=status.HTTP_400_BAD_REQUEST)

        if username is None:
            return Response({'error': 'Unable to find student'}, status=status.HTTP_404_NOT_FOUND)

        return func(self, request, username=username, *args, **kwargs)

    return extract_username_impl
