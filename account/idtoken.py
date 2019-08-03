from django.conf import settings
from django.contrib.auth.models import User

import datetime
import jwt

def generate_id_token(user):
  """
  Generates an identification token for the specified user and returns it.
  """
  expiry = datetime.datetime.utcnow() + datetime.timedelta(days=10)
  expiry = expiry.replace(second=0, microsecond=0, minute=0, hour=6)
  return jwt.encode({'u': user.id, 'exp': expiry}, settings.SECRET_KEY, algorithm='HS256')

def read_id_token(token):
  """
  Reads an identification token and returns the user it was generated for.
  """
  try:
    data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    user = User.objects.get(id=data['u'])
    return user
  except jwt.ExpiredSignatureError:
    return None
  except User.DoesNotExist:
    return None
