from django.contrib.auth.models import AbstractUser
from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?


# models.PROTECT says to forbid the deletion of the referenced object. To delete it we ahve to manually delete all
# references.


class Klass(models.Model):
    instructor = models.ForeignKey('profiles.Instructor', related_name='klasses', on_delete=models.PROTECT)
    students = models.ManyToManyField('profiles.ChaUser', through='profiles.StudentMembership')

    teacher_assistants = models.ManyToManyField('profiles.Instructor', through='profiles.AssistantMembership')

    name = models.CharField(max_length=60, null=False, blank=False, default="New Course")
    course_number = models.SlugField(max_length=60, null=False, blank=False, unique=True, default=None)
