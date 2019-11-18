import logging

from django import template
from django.core.exceptions import ObjectDoesNotExist

from apps.homework.models import Submission

register = template.Library()
logger = logging.getLogger(__name__)


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


register.filter('get_submission', get_submission)
register.filter('format_json_array', format_json_array)
