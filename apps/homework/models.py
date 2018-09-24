from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?


class HomeworkDefinition(models.Model):
    klass = models.ForeignKey('klasses.Klass', related_name='homework_defintions', on_delete=models.PROTECT)
    creator = models.ForeignKey('profiles.Instructor', related_name='created_homework_defintions', on_delete=models.PROTECT)


class HomeworkSubmission(models.Model):
    klass = models.ForeignKey('klasses.Klass', related_name='homework_submissions', on_delete=models.PROTECT)
    creator = models.ForeignKey('profiles.Instructor', related_name='created_homework_submissions', on_delete=models.PROTECT)


class HomeworkGrade(models.Model):
    submission = models.OneToOneField('HomeworkSubmission', related_name='grade', on_delete=models.PROTECT)
    evaluator = models.ForeignKey('profiles.Instructor', related_name='assigned_grades', on_delete=models.PROTECT)
