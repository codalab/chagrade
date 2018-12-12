import os
from urllib.parse import urlparse

import requests
from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?
from requests.auth import HTTPBasicAuth


class Definition(models.Model):
    klass = models.ForeignKey('klasses.Klass', related_name='homework_definitions', on_delete=models.PROTECT)
    creator = models.ForeignKey('profiles.Instructor', related_name='created_homework_defintions', on_delete=models.PROTECT)

    due_date = models.DateTimeField(default=None)

    name = models.CharField(default=None, max_length=100, null=False, blank=False)
    description = models.CharField(max_length=300, null=True, blank=True)

    challenge_url = models.URLField(default=None, null=True, blank=True)
    starting_kit_github_url = models.URLField(default=None, null=True, blank=True)

    # These values for submissions will have to be grabbed from v1.5 API
    # We should almost set these automatically by an API request to the challenge and see if these options are enabled
    #  or not?
    ask_method_name = models.BooleanField(default=False)
    ask_method_description = models.BooleanField(default=False)
    ask_project_url = models.BooleanField(default=False)
    ask_publication_url = models.BooleanField(default=False)

    team_based = models.BooleanField(default=False)

    class Meta:
        unique_together = ('klass', 'name')

    def __str__(self):
        return "{}".format(self.name)

    def get_challenge_domain(self):
        parsed_uri = urlparse(self.challenge_url)
        scheme = parsed_uri.scheme
        domain = parsed_uri.netloc
        site_url = "{0}://{1}".format(scheme, domain)
        return site_url


class Submission(models.Model):
    klass = models.ForeignKey('klasses.Klass', default=None, related_name='homework_submissions', on_delete=models.PROTECT)
    definition = models.ForeignKey('Definition', default=None, related_name='submissions', on_delete=models.PROTECT)
    creator = models.ForeignKey('profiles.StudentMembership', related_name='submitted_homeworks', on_delete=models.PROTECT)

    submission_github_url = models.URLField(default=None, null=True, blank=True)

    method_name = models.CharField(max_length=100, default='', null=True, blank=True)
    method_description = models.CharField(max_length=300, default='', null=True, blank=True)
    project_url = models.URLField(max_length=200, default='', null=True, blank=True)
    publication_url = models.URLField(max_length=200, default='', null=True, blank=True)

    submitted_to_challenge = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.submission_github_url)


class SubmissionTracker(models.Model):
    submission = models.ForeignKey('Submission', related_name='tracked_submissions', null=True, blank=True, on_delete=models.CASCADE)

    remote_id = models.CharField(max_length=10)
    remote_phase = models.CharField(max_length=10)

    def get_remote_submission_info(self):
        challenge_site_url = self.submission.definition.get_challenge_domain()
        score_api_url = "{0}/api/submission/{1}/get_score".format(challenge_site_url, self.remote_id)
        score_api_resp = requests.get(
            score_api_url,
            auth=HTTPBasicAuth(
                os.environ.get('CODALAB_SUBMISSION_USERNAME'),
                os.environ.get('CODALAB_SUBMISSION_PASSWORD')
            )
        )
        if score_api_resp.status_code == 200:
            data = score_api_resp.json()
            if data.get('status'):
                print("Data found for submission. Returning scores.")
                return {
                    'status': data.get('status'),
                    'score': data.get('score')
                }
            else:
                print("Could not retrieve complete data for submission")
                return None
        elif score_api_resp.status_code == 404:
            print("Could not find submission or competition.")
            return None
        elif score_api_resp.status_code == 403:
            print("Not authorized to make this request.")
            return None
        print("There was a problem making the request")
        return None


class Grade(models.Model):
    submission = models.ForeignKey('Submission', related_name='grades', on_delete=models.CASCADE)
    evaluator = models.ForeignKey('profiles.Instructor', related_name='assigned_grades', on_delete=models.PROTECT)
    # criteria = models.OneToOneField('Criteria', related_name='grade', on_delete=models.PROTECT)
    # criteria = models.OneToOneField('Criteria', related_name='grade', on_delete=models.PROTECT)

    # overall_grade = models.IntegerField(default=0)
    overall_grade = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    teacher_comments = models.CharField(max_length=400, default='', null=True, blank=True)
    instructor_notes = models.CharField(max_length=400, default='', null=True, blank=True)

    def __str__(self):
        return "{0}:{1}".format(self.submission.submission_github_url, self.evaluator.user.username)

    def calculate_grade(self):
        # new_obj = serializer.save()
        # grade = Grade.objects.get(pk=grade_pk)
        total = 0
        total_possible = 0
        # Average should be total points scored over total points possible
        for criteria_answer in self.criteria_answers.all():
            print(criteria_answer.criteria.upper_range)
            total_possible += criteria_answer.criteria.upper_range
            total += criteria_answer.score
        if total_possible == 0 or total == 0:
            print("0")
            # return 0
            self.overall_grade = 0
        else:
            print("Returning an actual grade")
            # return total / total_possible
            self.overall_grade = total / total_possible
            print(self.overall_grade)
        print("Calling save")
        self.save()
        print(self.overall_grade)


class Question(models.Model):
    definition = models.ForeignKey('Definition', related_name='custom_questions', on_delete=models.CASCADE)

    has_specific_answer = models.BooleanField(default=False)

    question = models.CharField(max_length=300)
    answer = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.question


class Criteria(models.Model):
    definition = models.ForeignKey('Definition', related_name='criterias', on_delete=models.CASCADE)

    description = models.CharField(max_length=150, default='')
    lower_range = models.IntegerField(default=0)
    upper_range = models.IntegerField(default=10)

    def __str__(self):
        return "{0}-{1}".format(self.definition, self.pk)


class QuestionAnswer(models.Model):
    submission = models.ForeignKey('Submission', related_name='question_answers', on_delete=models.PROTECT)
    question = models.ForeignKey('Question', default=None, related_name='student_answers', on_delete=models.PROTECT)

    # definition = models.ForeignKey('Definition', related_name='student_answers', on_delete=models.CASCADE)

    text = models.CharField(max_length=150, default='')
    is_correct = models.BooleanField(default=False)


class CriteriaAnswer(models.Model):
    # submission = models.ForeignKey('Submission', related_name='criteria_answers', on_delete=models.CASCADE)
    grade = models.ForeignKey('Grade', default=None, related_name='criteria_answers', on_delete=models.CASCADE)
    criteria = models.ForeignKey('Criteria', related_name='answers', on_delete=models.CASCADE)
    # text = models.CharField(max_length=150, default='')
    score = models.IntegerField(default=0)
    # evaluator = models.ForeignKey('profiles.Instructor', related_name='criteria_answers', on_delete=models.PROTECT)
