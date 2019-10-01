import os
from urllib.parse import urlparse

import requests

from django.db import models
from django.contrib.postgres.fields import JSONField

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?
from requests.auth import HTTPBasicAuth

from apps.homework.validators import validate_submission_github_url


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

    def get_challenge_url(self):
        parsed_uri = urlparse(self.challenge_url)
        scheme = parsed_uri.scheme
        domain = parsed_uri.netloc
        site_url = "{0}://{1}".format(scheme, domain)
        return site_url


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

    created = models.DateTimeField(auto_now_add=True)

    submitted_to_challenge = models.BooleanField(default=False)

    team = models.ForeignKey('groups.Team', default=None, null=True, blank=True, related_name='submissions', on_delete=models.SET_NULL)

    def __str__(self):
        return "{}".format(self.github_url)

    @property
    def get_challenge_url(self):
        if not self.definition.challenge_url:
            print("No challenge URL given.")
            return
        if not self.github_url:
            print("No submission github URL given.")
            return
        if self.definition.team_based:
            if not self.team:
                print("Team not set")
                return
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
        self.stored_status = None
        self.stored_score = None

        if score_api_resp.status_code == 200:
            data = score_api_resp.json()
            if data.get('status'):
                self.stored_status = data.get('status')
                self.stored_score = float(data.get('score', None))

        self.save()
        return

    @property
    def status(self):
        if self.stored_status:
            self.retrieve_score_and_status()
        return self.stored_status

    @property
    def score(self):
        if self.stored_score == None:
            self.retrieve_score_and_status()
        return self.stored_score


class Grade(models.Model):
    submission = models.ForeignKey('Submission', related_name='grades', on_delete=models.CASCADE)
    evaluator = models.ForeignKey('profiles.Instructor', related_name='assigned_grades', on_delete=models.CASCADE)

    overall_grade = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    text_grade = models.CharField(max_length=10, null=True, blank=True, default="0/0")

    teacher_comments = models.CharField(max_length=400, default='', null=True, blank=True)
    instructor_notes = models.CharField(max_length=400, default='', null=True, blank=True)

    published = models.BooleanField(default=False)

    def __str__(self):
        return "{0}:{1}".format(self.submission.github_url, self.evaluator.user.username)

    def get_total_score_total_possible(self):
        total_possible = 0
        total = 0
        for criteria_answer in self.criteria_answers.all():
            total_possible += criteria_answer.criteria.upper_range
            total += criteria_answer.score
        return total, total_possible

    def calculate_grade(self):
        total, total_possible = self.get_total_score_total_possible()
        self.text_grade = f"{total}/{total_possible}"
        if total_possible != 0 and total != 0:
            self.overall_grade = total/total_possible
        self.save()


class Question(models.Model):
    MULTIPLE_SELECT = 'MS'
    SINGLE_SELECT = 'SS'
    TEXT = 'TX'

    TYPE_CHOICES = [
        (MULTIPLE_SELECT, 'Checkboxes'),
        (SINGLE_SELECT, 'Multiple Choice'),
        (TEXT, 'Text Answer'),
    ]
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=TEXT)

    definition = models.ForeignKey('Definition', related_name='custom_questions', on_delete=models.CASCADE)

    has_specific_answer = models.BooleanField(default=False)

    question = models.CharField(max_length=300)
#    answer = models.TextField(blank=True, default='')
    candidate_answers = JSONField(blank=True, default='')

    # If Question is a single or multiple select is the type of the question, the candidate answers are in the
    # form of an array in JSON. The student's selection(s) are stored on the Question Answer model in the form
    # of indices that refer to entries in this candidate answer array.
    #
    # E.g. If a question had a prompt that looked like this, "What is 5 + 5?", the candidate answers could look
    # like the following:
    #
    # candidate_answers = [
    #     '2',
    #     '3',
    #     '8',
    #     '10',
    # ]
    #
    # The student's answer would be stored in the following form on the QuestionAnswer model:
    # QuestionAnswer = {
    #     'answer': 3
    # }
    #
    #
    #
    # If the Question is a 'Text Answer', the candidate_answers object would either be left blank or take
    # the following form:
    #
    # Question: "What is my favorite color?"
    #
    # candidate_answers = {
    #     'red'
    # }
    #
    # The student's answer would be stored like this:
    # answer = {
    #     'text': 'green'
    # }

    def __str__(self):
        return self.question


class QuestionAnswer(models.Model):
    submission = models.ForeignKey('Submission', related_name='question_answers', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', default=None, related_name='student_answers', on_delete=models.CASCADE)

    #text = models.TextField(default='')
    answer = JSONField(default='')
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
