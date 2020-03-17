import os
from urllib.parse import urlparse

import requests
import logging
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two separate sub-models from this one?
from requests.auth import HTTPBasicAuth

from apps.homework.validators import validate_submission_github_url

logger = logging.getLogger(__name__)


class Definition(models.Model):
    klass = models.ForeignKey('klasses.Klass', related_name='homework_definitions', on_delete=models.CASCADE)
    creator = models.ForeignKey('profiles.Instructor', related_name='created_homework_defintions', on_delete=models.CASCADE)

    due_date = models.DateTimeField(default=None)

    name = models.CharField(default=None, max_length=100, null=False, blank=False)
    description = models.CharField(max_length=300, null=True, blank=True)

    questions_only = models.BooleanField(default=False, null=False)

    challenge_url = models.URLField(default=None, null=True, blank=True)
    starting_kit_github_url = models.URLField(default=None, null=True, blank=True)

    # Make required if not questions_only
    baseline_score = models.FloatField(default=0.0, null=True, blank=False)
    target_score = models.FloatField(default=1.0, null=True, blank=False)

    max_submissions_per_student = models.IntegerField(default=20, null=False, validators=[MaxValueValidator(40), MinValueValidator(0)])
    force_github = models.BooleanField(default=False)

    # Jupyter Notebook Grading Parameters
    jupyter_notebook_enabled = models.BooleanField(default=False)
    jupyter_notebook_lowest = models.FloatField(default=0.0, null=True, blank=False)
    jupyter_notebook_highest = models.FloatField(default=1.0, null=True, blank=False)

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
        ordering = ['name']

    def __str__(self):
        return "{}".format(self.name)

    def get_challenge_url(self):
        parsed_uri = urlparse(self.challenge_url)
        scheme = parsed_uri.scheme
        domain = parsed_uri.netloc
        site_url = "{0}://{1}".format(scheme, domain)
        return site_url


def upload_jupyter_notebook(instance, filename):
    file_split = filename.split('.')
    file_extension = file_split[len(file_split) - 1]
    path = f'jupyter_notebooks/submissions/{instance.pk}.{file_extension}'
    return path


class Submission(models.Model):
    klass = models.ForeignKey('klasses.Klass', default=None, related_name='homework_submissions', on_delete=models.CASCADE)
    definition = models.ForeignKey('Definition', default=None, related_name='submissions', on_delete=models.CASCADE)
    creator = models.ForeignKey('profiles.StudentMembership', related_name='submitted_homeworks', on_delete=models.CASCADE)

    github_url = models.URLField(default=None, null=True, blank=True, validators=[validate_submission_github_url])
    github_repo_name = models.CharField(max_length=150, default='', blank=True)
    github_branch_name = models.CharField(max_length=150, default='', blank=True)
    github_commit_hash = models.CharField(max_length=50, default='', blank=True)

    method_name = models.CharField(max_length=100, default='', null=True, blank=True)
    method_description = models.CharField(max_length=300, default='', null=True, blank=True)
    project_url = models.URLField(max_length=200, default='', null=True, blank=True)
    publication_url = models.URLField(max_length=200, default='', null=True, blank=True)

    is_direct_upload = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    submitted_to_challenge = models.BooleanField(default=False)

    team = models.ForeignKey('groups.Team', default=None, null=True, blank=True, related_name='submissions', on_delete=models.SET_NULL)

    jupyter_notebook = models.FileField(null=True, blank=True, upload_to=upload_jupyter_notebook)
    jupyter_score = models.FloatField(null=True)

    reporting_messages = JSONField(default=dict)
    # Reporting messages is used to report warnings and errors on the submission during the automatic Jupyter Notebook grading process.
    # This field should take the form of:
    # {
    #     'warnings': ['warning string 1', 'warning string 2'],
    #     'errors': ['error string 1', 'error string 2'],
    # }

    def __str__(self):
        return "{}".format(self.github_url)

    @property
    def get_challenge_url(self):
        if not self.definition.challenge_url:
            print("No challenge URL given.")
            return
        if self.definition.team_based:
            if not self.team:
                print("Team not set")
                return self.definition.challenge_url
            custom_urls = self.team.challenge_urls.filter(definition=self.definition)
            if not custom_urls:
                print("No custom URL found, returning definition challenge url")
                return self.definition.challenge_url
            else:
                print("Returning found custom url")
                return custom_urls.first().challenge_url
        else:
            return self.definition.challenge_url

    def filename(self):
        return self.github_url.split('/')[-1]


class SubmissionTracker(models.Model):
    submission = models.ForeignKey('Submission', related_name='tracked_submissions', null=True, blank=True, on_delete=models.CASCADE)

    stored_status = models.CharField(max_length=20, null=True)
    stored_score = models.FloatField(null=True)

    remote_id = models.CharField(max_length=10)
    remote_phase = models.CharField(max_length=10)

    stored_logs = JSONField(default=dict, null=True, blank=True)

    def retrieve_score_and_status(self):
        challenge_site_url = self.submission.definition.get_challenge_url()
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
                self.stored_status = data.get('status')
                self.stored_score = float(data.get('score', 0))
                self.stored_logs = data.get('logs')
        self.save()
        return

    @property
    def status(self):
        bad_statuses = [None, "Submitted", "Running"]
        if self.stored_status in bad_statuses:
            self.retrieve_score_and_status()
        return self.stored_status

    @property
    def score(self):
        if self.stored_score == None:
            self.retrieve_score_and_status()
        return self.stored_score

    @property
    def logs(self):
        if self.stored_logs == None or len(self.stored_logs.keys()) == 0:
            self.retrieve_score_and_status()
        else:
            # Try the first URL in our logs
            sas_url = self.stored_logs[list(self.stored_logs.keys())[0]]
            resp = requests.get(sas_url)
            if not resp.ok:
                logger.info("Submission SAS urls for logs appear expired, retrieving new ones.")
                self.retrieve_score_and_status()
        return self.stored_logs


class Grade(models.Model):
    submission = models.ForeignKey('Submission', related_name='grades', on_delete=models.CASCADE)
    evaluator = models.ForeignKey('profiles.Instructor', related_name='assigned_grades', on_delete=models.CASCADE)

    overall_grade = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    text_grade = models.CharField(max_length=20, null=True, blank=True, default="0/0")

    teacher_comments = models.TextField(default='', null=True, blank=True)
    instructor_notes = models.TextField(default='', null=True, blank=True)

    published = models.BooleanField(default=False)

    needs_review = models.BooleanField(default=True)
    jupyter_notebook_grade = models.FloatField(null=True)

    def __str__(self):
        return "{0}:{1}".format(self.submission.github_url, self.evaluator.user.username)

    def get_total_score_total_possible(self):
        total_possible = self.get_total_possible()
        total = self.get_total_score()
        return total, total_possible

    def get_total_possible(self):
        total_possible = 0
        for criteria_answer in self.criteria_answers.all():
            total_possible += criteria_answer.criteria.upper_range
        if self.submission.definition.jupyter_notebook_enabled:
            total_possible += self.submission.definition.jupyter_notebook_highest
        return total_possible

    def get_total_score(self):
        total = 0
        for criteria_answer in self.criteria_answers.all():
            total += criteria_answer.score
        if self.submission.definition.jupyter_notebook_enabled:
            total += self.jupyter_notebook_grade or 0.0
        return total

    def calculate_grade(self):
        total, total_possible = self.get_total_score_total_possible()
        self.text_grade = f"{total}/{total_possible}"
        if total_possible != 0 and total is not None:
            self.overall_grade = total / total_possible
            self.save()
            return self.overall_grade
        self.save()
        return None


class Question(models.Model):
    """
    If Question is of question_type: single select or multiple select, the candidate answers are in the
    form of an array in JSON. The student's selection(s) are stored on the Question Answer model.

    E.g. If a question had a prompt that looked like this, "What is 5 + 5?", the candidate answers could look
    like the following:

    candidate_answers = [
        '2',
        '3',
        '8',
        '10',
    ]

    The student's answer would be stored in the following form on the QuestionAnswer model:
    QuestionAnswer = {
        'answer': '10
    }



    If the Question is a 'Text Answer', the candidate_answers object would either be left blank or take
    the following form:

    Question: "What is my favorite color?"

    candidate_answers = {
        'red'
    }

    The student's answer would be stored like this:
    answer = {
        'text': 'green'
    }
    """

    MULTIPLE_SELECT = 'MS'
    SINGLE_SELECT = 'SS'
    TEXT = 'TX'

    TYPE_CHOICES = [
        (MULTIPLE_SELECT, 'Checkboxes'),
        (SINGLE_SELECT, 'Multiple Choice'),
        (TEXT, 'Text Answer'),
    ]
    question_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=TEXT)

    definition = models.ForeignKey('Definition', related_name='custom_questions', on_delete=models.CASCADE)

    has_specific_answer = models.BooleanField(default=False)

    question = models.CharField(max_length=300)
    candidate_answers = JSONField(blank=True, default=list)

    def __str__(self):
        return self.question


class QuestionAnswer(models.Model):
    submission = models.ForeignKey('Submission', related_name='question_answers', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', default=None, related_name='student_answers', on_delete=models.CASCADE)

    answer = JSONField(default=dict)
    is_correct = models.BooleanField(default=False)


class Criteria(models.Model):
    definition = models.ForeignKey('Definition', related_name='criterias', on_delete=models.CASCADE)

    description = models.CharField(max_length=150, default='')
    lower_range = models.IntegerField(default=0)
    upper_range = models.IntegerField(default=10)

    def __str__(self):
        return "{0}-{1}".format(self.definition, self.pk)


class CriteriaAnswer(models.Model):
    grade = models.ForeignKey('Grade', default=None, related_name='criteria_answers', on_delete=models.CASCADE)
    criteria = models.ForeignKey('Criteria', related_name='answers', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)


class TeamCustomChallengeURL(models.Model):
    team = models.ForeignKey('groups.Team', related_name='challenge_urls', on_delete=models.CASCADE)
    definition = models.ForeignKey(Definition, related_name='custom_challenge_urls', on_delete=models.CASCADE)
    challenge_url = models.URLField()
