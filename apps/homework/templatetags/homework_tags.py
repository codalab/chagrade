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
            if definition.team_based:
                return definition.submissions.filter(team=student.team).last()
            else:
                return definition.submissions.filter(creator=student).last()
        except ObjectDoesNotExist:
            print("Could not find an object matching that query")
    return None


def get_last_team_submission(definition, user_pk):
    if definition and definition.team_based and user_pk:
        try:
            user = ChaUser.objects.get(pk=user_pk)
            student = StudentMembership.objects.get(user=user, klass=definition.klass)
            return definition.submissions.filter(team=student.team).last()
        except ObjectDoesNotExist:
            print("Could not find an object matching that query")
    return None


def get_last_grade(submission):
        if submission:
            if submission.grades.filter(published=True).count() > 0:
                return submission.grades.filter(published=True).last()
        return None


def get_last_grade_teacher(submission):
    if submission:
        if submission.grades.count() > 0:
            return submission.grades.last()
    return None


def get_item(dictionary, key):
    return dictionary.get(key)

def previous(some_list, current_index):
    try:
        return some_list[int(current_index) - 1]
    except IndexError:
        return ''

def next(some_list, current_index):
    try:
        return some_list[int(current_index) + 1]
    except IndexError:
        return ''

register.filter('get_last_submission', get_last_submission)
register.filter('get_last_grade', get_last_grade)
register.filter('get_last_grade_teacher', get_last_grade_teacher)
register.filter('get_item', get_item)
register.filter('previous', previous)
register.filter('next', next)
