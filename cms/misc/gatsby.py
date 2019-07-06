from requests import post, get
from django.conf import settings

def gatsby_manager(update = False):
  """View for gatsby build page"""

  url = settings.GATSBY_MANAGER_URL

  if update:
    r = post(url)
  else:
    r = get(url)
  
  return r.json()