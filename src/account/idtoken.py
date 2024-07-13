from django.contrib.auth.models import User
from django.core.signing import Signer

import datetime

def generate_id_token(user):
  """
  Generates an identification token for the specified user and returns it.
  """
  expiry = datetime.datetime.utcnow() + datetime.timedelta(days=10)
  expiry = expiry.replace(second=0, microsecond=0, minute=0, hour=6)
  signer = Signer(salt="sldkfa")
  encoded = signer.sign(str(int(expiry.timestamp())) + "," + str(user.id))
  return encoded

def read_id_token(token):
  """
  Reads an identification token and returns the user it was generated for.
  """
  signer = Signer(salt="sldkfa")
  data = signer.unsign(token).split(",")
  now = datetime.datetime.utcnow().timestamp()
  if now > int(data[0]):
    return None
  try:
    return User.objects.get(id=data[1])
  except User.DoesNotExist:
      return None

