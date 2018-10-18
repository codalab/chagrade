from django.contrib.auth.models import AbstractUser
from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?


# models.PROTECT says to forbid the deletion of the referenced object. To delete it we ahve to manually delete all
# references.
from django.utils import timezone


class Klass(models.Model):
    # COMPLETE = 'complete'
    # INCOMPLETE = 'incomplete'

    instructor = models.ForeignKey('profiles.Instructor', related_name='klasses', on_delete=models.PROTECT)
    students = models.ManyToManyField('profiles.ChaUser', through='profiles.StudentMembership')

    teacher_assistants = models.ManyToManyField('profiles.Instructor', through='profiles.AssistantMembership')

    title = models.CharField(max_length=60, null=False, blank=False, default="New Course")
    course_number = models.SlugField(max_length=60, null=False, blank=False, unique=True, default=None)
    description = models.CharField(max_length=300, null=True, blank=True, default="")

    created = models.DateTimeField(editable=False, default=timezone.now, null=True, blank=True)
    modified = models.DateTimeField(default=timezone.now, null=True, blank=True)

    # Don't like this related name but we already used .klasses
    group = models.ForeignKey('groups.InstructorGroup', related_name='klasses', null=True, blank=True, on_delete=models.PROTECT)

    image = models.ImageField(null=True, blank=True)
    syllabus = models.FileField(null=True, blank=True)

    active = models.BooleanField(default=False)

    # status = models.CharField(max_length=60,)

    def __str__(self):
        return "{0} by {1}".format(self.course_number, self.instructor.user.username)

    @property
    def status(self):
        return "NOT-IMPLEMENTED"

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)
