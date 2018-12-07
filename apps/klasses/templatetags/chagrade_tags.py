from django import template
from django.core.exceptions import ObjectDoesNotExist

from apps.homework.models import Submission

register = template.Library()


def get_submission(definition_pk, student_pk):
    """Gets a submission given a definition and a student"""
    try:
        sub = Submission.objects.filter(definition__pk=definition_pk, creator__pk=student_pk).first()
        if sub:
            return sub
    except ObjectDoesNotExist:
        print("Could not find a submission for that definition/student!")
    return None

register.filter('get_submission', get_submission)
