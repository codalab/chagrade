import logging
import re

from django import template
from django.core.exceptions import ObjectDoesNotExist

from apps.homework.models import Submission

register = template.Library()
logger = logging.getLogger(__name__)


def format_url_with_schema(url):
    if type(url) == str:
        if not re.match('(?:http|https)://', url):
            return 'http://{}'.format(url)
    return url


def format_as_int(number):
    if number is not None:
        return int(number)
    else:
        return number


def get_submission(definition_pk, student_pk):
    """Gets a submission given a definition and a student"""
    try:
        sub = Submission.objects.filter(definition__pk=definition_pk, creator__pk=student_pk).first()
        if sub:
            return sub
    except ObjectDoesNotExist:
        logger.info("Could not find a submission for that definition/student!")
    return None


def format_json_array(json_array):
    """Formats list (json array) as a string by appending each item together."""
    outstring = ''
    delimiter = ',\n'

    for i, word in enumerate(json_array):
        if i < len(json_array) - 1:
            outstring += str(word) + delimiter
        else:
            outstring += str(word)
    return outstring


register.filter('format_as_int', format_as_int)
register.filter('format_url_with_schema', format_url_with_schema)
register.filter('get_submission', get_submission)
register.filter('format_json_array', format_json_array)
