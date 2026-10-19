from django.shortcuts import redirect


def index(_request):
    return redirect("admin:index")
