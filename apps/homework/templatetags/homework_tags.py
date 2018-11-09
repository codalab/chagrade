from django import template
from django.core.exceptions import ObjectDoesNotExist
from apps.homework.models import Definition
from apps.profiles.models import ChaUser, StudentMembership

register = template.Library()


def get_last_submission(definition, user_pk):
    try:
        # print("@@@@@@@@@@@@@@")
        # print(definition)
        # print(user_pk)
        # print("@@@@@@@@@@@@@@")
        # definition = Definition.objects.get(pk=definition_pk)
        user = ChaUser.objects.get(pk=user_pk)
        # print(user)
        student = StudentMembership.objects.get(user=user, klass=definition.klass)
        # print(student)
        # print(definition.submissions.all())
        # print(definition.submissions.first())
        # sub = definition.submissions.all().filter(creator=student).last()
        # Gets us the last one by pk
        # sub = definition.submissions.filter(creator=student).first()
        # print(definition.submissions.filter(creator=student).first())
        # print(sub)
        # return sub
        print(definition.submissions.first().creator)
        # print(definition.submissions.filter(creator=student).first())
        return definition.submissions.filter(creator=student).first()
    except ObjectDoesNotExist:
        return None


def get_last_grade(submission):
        if submission:
            if submission.grades.count() > 0:
                return submission.grades.first()
        return None

register.filter('get_last_submission', get_last_submission)
register.filter('get_last_grade', get_last_grade)
