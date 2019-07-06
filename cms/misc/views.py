from django.shortcuts import render

from requests import post, get
from django.conf import settings
from .gatsby import gatsby_manager

def gatsby(request):
  """View for gatsby build page"""
  d = gatsby_manager(request.method == "POST")

  return render(request, 'gatsby/base.html', {
    "running": d['running'],
    "log": d['log'],
    "start_time": d['started'],
    "finish_time": d['finished']
  })