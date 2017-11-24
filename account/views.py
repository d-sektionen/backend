from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect

from rest_framework_jwt.settings import api_settings


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
