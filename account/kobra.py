import logging

import requests
from django.conf import settings

BASE_URL = 'https://kobra.karservice.se'
QUERY_URL = BASE_URL + '/api/v1/students/{}'

token = settings.KOBRA_TOKEN
logger = logging.getLogger(__name__)
if settings.TESTING:
    logger.setLevel(logging.ERROR)


def liu_id_from_card(card_id):
    """
    Takes the id that is on the liu cards and gets the liu id from Kobra.
    :param card_id: (int) The identification number that can be acquired from the liu card via a RFID card reader.
    :return: (string) The liu id of the user with the card id card_id.
    """
    if token is None:
        logger.warning('Unable to authenticate with Kobra (have you set KOBRA_TOKEN?)')
        return None

    r = requests.get(QUERY_URL.format(card_id), headers={'Authorization': 'Token ' + token})
    if r.status_code == 200:
        return r.json().get('liu_id')
    else:
        return None


def name_from_liu_id(liu_id):
    if token is None:
        logger.warning('Unable to authenticate with Kobra (have you set KOBRA_TOKEN?)')
        return None, None

    print('Query url: "%s"' % QUERY_URL.format(liu_id))
    r = requests.get(QUERY_URL.format(liu_id), headers={'Authorization': 'Token ' + token})
    print(r.content)
    if r.status_code == 200:
        full_name = r.json().get('name')
        i = full_name.index(' ')  # First space index

        first_name = full_name[:i]
        last_name = full_name[i+1:]

        return first_name, last_name
    else:
        return None, None


def is_student(username):
    firstname, lastname = name_from_liu_id(username)

    return firstname is not None
