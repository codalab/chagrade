from celery.task import task
from django.core.exceptions import ObjectDoesNotExist

from apps.homework.models import Grade


@task
def calculate_new_grade(grade_pk):
    print("!!!!!!!!!!!!!!!!")
    print(grade_pk)
    print("!!!!!!!!!!!!!!!!")
    try:
        grade = Grade.objects.get(pk=grade_pk)
        total = 0
        total_possible = 0
        # Average should be total points scored over total points possible
        for criteria_answer in grade.criteria_answers.all():
            total_possible += criteria_answer.criteria.upper_range
            total = criteria_answer.score
        if total_possible == 0 or total == 0:
            print("0")
            # return 0
            grade.overall_grade = 0
        else:
            print("Returning an actual grade")
            # return total / total_possible
            grade.overall_grade = total / total_possible
        print("Calling save")
        grade.save()
    except ObjectDoesNotExist:
        print("Could not compute")