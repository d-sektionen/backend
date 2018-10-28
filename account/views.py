from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from rest_framework_jwt.settings import api_settings

from account.models import Section
from account.serializers import UserSerializer, DetailedSectionSerializer
from app.decorators import extract_user


@login_required
def generate_token(request):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    payload = jwt_payload_handler(request.user)
    token = jwt_encode_handler(payload)

    if 'redirect' in request.GET:
        redirect_url = request.GET['redirect']
        if '?' in redirect_url:
            redirect_url += '&token=' + token
        else:
            redirect_url += '?token=' + token

        return redirect(redirect_url)
    else:
        return JsonResponse({
            'token': token
        })


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    # def retrieve(self, request, *args, **kwargs):
    #     if kwargs['pk'] == 'me':
    #         serializer = self.get_serializer(request.user)
    #         return Response(serializer.data)
    #     else:
    #         return super(UserViewSet, self).retrieve(request, *args, **kwargs)
    #
    # def update(self, request, *args, **kwargs):
    #     print(request)
    #     print(request.data)
    #     print("loooooooooooooooooooooooooooooooooooool")
    #     print(kwargs)
    #     if kwargs['pk'] == 'me':
    #         instance = request.user
    #         serializer = self.serializer_class(instance, data=request.data, partial=True)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data)
    #     else:
    #         return super(UserViewSet, self).update(request, *args, **kwargs)


# class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#
#     def retrieve(self, request, *args, **kwargs):
#         if kwargs['pk'] == 'me':
#             serializer = self.get_serializer(request.user)
#             return Response(serializer.data)
#         else:
#             return super(UserViewSet, self).retrieve(request, *args, **kwargs)


class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = DetailedSectionSerializer

    def get_queryset(self):
        user = self.request.user
        user_groups = user.groups.all()
        sections = Section.objects.filter(admin_group__in=user_groups)

        return sections

    @extract_user
    def create(self, request, *args, **kwargs):
        section_id = request.data['section']
        section = Section.objects.get(id=section_id)
        user = kwargs['user']

        user.groups.add(section.admin_group)

        return Response(status=status.HTTP_201_CREATED)

    @list_route(methods=['delete'], url_path='')
    @extract_user
    def delete(self, request, *args, **kwargs):
        section_id = request.data['section']
        section = Section.objects.get(id=section_id)
        user = kwargs['user']

        user.groups.remove(section.admin_group)

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
