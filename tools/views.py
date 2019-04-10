from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from icalendar import Calendar, Event, vDatetime
import datetime
from django.utils import timezone
from django.conf import settings
from account.permissions import AllowSectionMembers
from logger.utils import log, Entry

import requests
import json

NETLIGHT_API_URL = settings.NETLIGHT_API_URL
NETLIGHT_API_KEY = settings.NETLIGHT_API_KEY
NETLIGHT_LOCK_ID = settings.NETLIGHT_LOCK_ID
NETLIGHT_AUTHORIZATION = settings.NETLIGHT_AUTHORIZATION

"""
Unlocks or locks the Netlight door.
"""
@api_view(['POST'])
@permission_classes((AllowSectionMembers,))
def netlight(request):
  mode = request.query_params.get('mode')
  hub_command = None

  if mode == 'unlock':
    hub_command = 0
  elif mode == 'lock':
    hub_command = 1
  else:
    return Response({'detail': 'Invalid mode parameter.'}, status=status.HTTP_400_BAD_REQUEST)

  headers = {
    'Content-Type': 'application/json',
    'APIKey': NETLIGHT_API_KEY,
    'Authorization': NETLIGHT_AUTHORIZATION
  }
  data = {
    'lockId': NETLIGHT_LOCK_ID,
    'hubCommand': hub_command
  }
  now = datetime.datetime.now()

  # Limit time of day when people can unlock door, they should still be able to lock at any time.
  todayMorningLimit = now.replace(hour=5, minute=0, second=0, microsecond=0)
  todayEveningLimit = now.replace(hour=21, minute=0, second=0, microsecond=0)
  notWithinLimits = now > todayEveningLimit or now < todayMorningLimit
  if (mode == 'unlock' and notWithinLimits): 
    return Response({'detail': 'Det går endast att låsa upp mellan ' + todayMorningLimit.strftime("%H:%M") + ' och ' + todayEveningLimit.strftime("%H:%M") + '.'}, status=status.HTTP_400_BAD_REQUEST)
  
  r = None
  # Log action and send request
  if (log(mode, Entry.NETLIGHT, user=request.user)):
    r = requests.post(NETLIGHT_API_URL, data=json.dumps(data), headers=headers)
  else:
    return Response({'detail': "Unable to log request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  # Respond to success
  if r.status_code == 200:
    msg = 'upplåst' if mode == 'unlock' else 'låst'
    return Response({'detail': "Dörren är nu på väg att bli " + msg + '.'}, status=status.HTTP_200_OK)

  # Respond to failed lock communication
  if r.status_code == 503:
    return Response({'detail': 'Låsservern kan inte nå låset. Se till att dosan är inkopplad.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
  if r.status_code == 401:
    return Response({'detail': 'Felkonfigurerad API_KEY eller AUTHORIZATION på servern.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  if r.status_code == 400:
    return Response({'detail': 'Felkonfigurerat LOCK_ID på servern.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  # If all other checks fail.
  return Response({'detail': 'Problem i kommunikationen med låset.','status': r.status_code}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


  
"""

"""
@api_view(['GET'])
@permission_classes((AllowSectionMembers,))
def member_only_accel_redirect(request):
  return Response({}, headers={'X-Accel-Redirect': request.query_params.get('url')})