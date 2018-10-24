from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?


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


class Submission(models.Model):
    klass = models.ForeignKey('klasses.Klass', related_name='homework_submissions', on_delete=models.PROTECT)
    creator = models.ForeignKey('profiles.StudentMembership', related_name='submitted_homework', on_delete=models.PROTECT)

    submission_github_url = models.URLField(default=None, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.submission_github_url)


class Grade(models.Model):
    submission = models.ForeignKey('Submission', related_name='grades', on_delete=models.CASCADE)
    evaluator = models.ForeignKey('profiles.Instructor', related_name='assigned_grades', on_delete=models.PROTECT)

    score = models.IntegerField(default=0)

    teacher_comments = models.CharField(max_length=400, default='', null=True, blank=True)
    instructor_notes = models.CharField(max_length=400, default='', null=True, blank=True)

    def __str__(self):
        return "{0}:{1}".format(self.submission.submission_github_url, self.score)


class Question(models.Model):
    HomeworkDefinition = models.ForeignKey('Definition', related_name='custom_questions', on_delete=models.CASCADE)

    has_specific_answer = models.BooleanField(default=False)

    question = models.CharField(max_length=300)
    answer = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.question


class Criteria(models.Model):
    # Automatic grading will not work without some more structure to how this should work...
    # We can check scores, execution time, etc
    # Analyzing code goes a bit far, but they will have to select from some pre-made options in order for us to decide
    # how to judge that/collect relevant data

    SCORE = 'score'
    DURATION = 'duration'
    TESTS = 'tests'

    criteria_type_choices = (
        (SCORE, 'Score'),
        (DURATION, 'duration'),
        (TESTS, 'tests')
    )

    homework_definition = models.ForeignKey('Definition', related_name='criterias', on_delete=models.CASCADE)

    criteria_type = models.CharField(choices=criteria_type_choices, max_length=20)

    # If we're within the range, score 100%, else score as score/upper-range: IE: 6/10 == 60%
    # This should leave teachers with multiple flexible ways to do this?
    # Brackets would be composite scores or Teachers would just hand grade as 100%, etc
    score_as_percent = models.BooleanField(default=True)

    lower_range = models.IntegerField(default=0)
    upper_range = models.IntegerField(default=10)

    def __str__(self):
        return "{0}-{1}".format(self.homework_definition, self.pk)
