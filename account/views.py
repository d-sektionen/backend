from django.http import JsonResponse

from account.sheet import Sheet


def index(request):
    sheet = Sheet()

    return JsonResponse({'user': request.user.username})
