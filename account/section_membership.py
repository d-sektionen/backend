"""
Provides an interface to the program registration API developed by LiU-IT.

Configuration (copied from d-authenticate.php)
-------------
Program codes can be found in the 'Studiehandbok' by inspecting the page url for the
requested program's 'Utbildningsplan'.

The 'Utbildningsplan' for the D program would look something like this
http://kdb-5.liu.se/liu/lith/studiehandboken/svutbplan.lasso?&up_year=2016&up_ladokkod=6CDDD

The program code can be found in the url parameter 'up_ladokkod'.

Relevant pages in the 'Studiehandbok'
https://www.lith.liu.se/sh/civing/index.html (civilingenjör)
https://www.lith.liu.se/sh/kand/index.html   (kandidatutbildning)
"""

import logging
import requests
from bs4 import BeautifulSoup
from django.conf import settings

SERVICE_URL = 'https://www4.student.liu.se/tentasearch/check_liuid_program?password=%s&liuid=%s%s'
SERVICE_KEY = settings.STUDENT_PORTAL_SERVICE_KEY
PROGRAM_CODE_FORMAT = '&programkoder=%s'

logger = logging.getLogger(__name__)


def check_membership(liu_id, section):
    """
    Checks if the given student is a member of the given section using the
    student portal API given by LiU-IT. All faults will be logged. Please note
    that the environment variable STUDENT_PORTAL_SERVICE_KEY must be set.
    """

    program_code_arguments = _build_program_code_arguments(section)
    verification_url = SERVICE_URL % (SERVICE_KEY, liu_id, program_code_arguments)

    response = requests.get(verification_url)
    if 200 <= response.status_code < 300:
        parsed_html = BeautifulSoup(response.content, 'html.parser')
        result_tag = parsed_html.body.find('result')
        if result_tag is not None:
            return result_tag.text != '0'
        else:
            logger.warning('Unable to authenticate with student portal (have you set STUDENT_PORTAL_SERVICE_KEY?)')
    else:
        logger.warning('Student portal API is not working properly (status code: %d)' % response.status_code)

    return False


def _build_program_code_arguments(section):
    """
    Constructs the program code arguments on the form: '&programkoder=A&programkoder=B&programkoder=C'
    """

    arguments = ''
    for program_code in section.get_program_codes():
        arguments += PROGRAM_CODE_FORMAT % program_code

    return arguments
