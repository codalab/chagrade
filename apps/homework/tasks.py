# import requests
from celery.task import task
# from django.core.exceptions import ObjectDoesNotExist
# from django.core.files.temp import TemporaryFile
#
# from apps.homework.models import Grade, Submission


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


# @task
# def post_submission(submission_pk):
#     submission = Submission.objects.get(pk=submission_pk)
#     # for line in urllib2.urlopen(submission.submission_github_url):
#     # temp_file = TemporaryFile()
#
#
# def download_file(url):
#     local_filename = url.split('/')[-1]
#     # NOTE the stream=True parameter
#     r = requests.get(url, stream=True)
#     # with open(local_filename, 'wb') as f:
#     # with
#     f = TemporaryFile()
#     # with TemporaryFile() as f:
#         # f.write('abcdefg')
#         # f.seek(0)  # go back to the beginning of the file
#         # print(f.read())
#         for chunk in r.iter_content(chunk_size=1024):
#             if chunk: # filter out keep-alive new chunks
#                 f.write(chunk)
#                 #f.flush() commented by recommendation from J.F.Sebastian
#     # return local_filename