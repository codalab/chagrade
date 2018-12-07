from django import template
from django.core.exceptions import ObjectDoesNotExist
from apps.homework.models import Definition
from apps.profiles.models import ChaUser, StudentMembership

register = template.Library()


def get_last_submission(definition, user_pk):
    if definition and user_pk:
        try:
            user = ChaUser.objects.get(pk=user_pk)
            student = StudentMembership.objects.get(user=user, klass=definition.klass)
            return definition.submissions.filter(creator=student).last()
        except ObjectDoesNotExist:
            print("Could not find an object matching that query")
    return None


def get_last_grade(submission):
        if submission:
            if submission.grades.count() > 0:
                return submission.grades.last()
        return None


def get_item(dictionary, key):
    return dictionary.get(key)

register.filter('get_last_submission', get_last_submission)
register.filter('get_last_grade', get_last_grade)
register.filter('get_item', get_item)
