from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response

from account import kobra
from account.user import get_or_create_user_if_student


def extract_user(func):
    @extract_username
    def extract_user_impl(self, request, *args, **kwargs):
        username = kwargs['username']
        print('extract_user_impl, username: ' + str(username))
        user = get_or_create_user_if_student(username)

        print('extract_user_impl, user: ' + str(user))

        if user is None:
            return Response({'error': 'Användaren är ingen student'}, status=status.HTTP_404_NOT_FOUND)

        return func(self, request, user=user, *args, **kwargs)

    return extract_user_impl


def extract_username(func):
    def extract_username_impl(self, request, *args, **kwargs):
        card_id = extract_data(request, 'card_id')
        username = extract_data(request, 'username')

        print('extract_username_impl, card_id: ' + str(card_id))
        print('extract_username_impl, username: ' + str(username))

        if card_id is not None:
            username = kobra.liu_id_from_card(card_id)
        elif username is None:
            return Response({'error': 'Missing required parameter username or card_id'}, status=status.HTTP_400_BAD_REQUEST)

        if username is None:
            return Response({'error': 'Unable to find student'}, status=status.HTTP_404_NOT_FOUND)

        return func(self, request, username=username, *args, **kwargs)

    return extract_username_impl


def extract_data(request, key):
    if key in request.data:
        return request.data[key]
    elif key in request.query_params:
        return request.query_params[key]
    else:
        return None
