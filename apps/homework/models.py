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
    klass = models.ForeignKey('klasses.Klass', default=None, related_name='homework_submissions', on_delete=models.PROTECT)
    definition = models.ForeignKey('Definition', default=None, related_name='submissions', on_delete=models.PROTECT)
    creator = models.ForeignKey('profiles.StudentMembership', related_name='submitted_homeworks', on_delete=models.PROTECT)

    submission_github_url = models.URLField(default=None, null=True, blank=True)

    method_name = models.CharField(max_length=100, default='', null=True, blank=True)
    method_description = models.CharField(max_length=300, default='', null=True, blank=True)
    project_url = models.URLField(max_length=200, default='', null=True, blank=True)
    publication_url = models.URLField(max_length=200, default='', null=True, blank=True)

    def __str__(self):
        return "{}".format(self.submission_github_url)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        print("This is getting called")
        super().save(force_insert, force_update, using, update_fields)


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

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     from apps.homework.tasks import calculate_new_grade
    #     super().save(force_insert=force_insert, force_update=force_update, using=using,
    #          update_fields=update_fields)
    #     # calculate_new_grade.delay(self.pk, countdown=3)
    #     print("@@@@@@@@@@@@@@@@@@@@@")
    #     print(self.pk)
    #     print(self.id)
    #     print("@@@@@@@@@@@@@@@@@@@@@")
    #     calculate_new_grade.apply_async(args=[self.pk], countdown=3)


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
