import uuid

from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?


# models.PROTECT says to forbid the deletion of the referenced object. To delete it we ahve to manually delete all
# references.
from django.utils import timezone


def upload_image(instance, filename):
    # path = "images/{0}/{1}_{2}".format(instance.id, filename, uuid.uuid4())
    file_split = filename.split('.')
    file_extension = file_split[len(file_split) - 1]
    print(file_extension)
    path = "images/{0}/class_image.{1}".format(instance.id, file_extension)
    return path


def upload_syllabus(instance, filename):
    # path = "images/{0}/{1}_{2}".format(instance.id, filename, uuid.uuid4())
    file_split = filename.split('.')
    file_extension = file_split[len(file_split) - 1]
    print(file_extension)
    path = "syllabuses/{0}/class_image.{1}".format(instance.id, file_extension)
    return path


class Klass(models.Model):
    # COMPLETE = 'complete'
    # INCOMPLETE = 'incomplete'

    instructor = models.ForeignKey('profiles.Instructor', related_name='klasses', on_delete=models.PROTECT)

    title = models.CharField(max_length=60, null=False, blank=False, default="New Course")
    course_number = models.SlugField(max_length=60, null=False, blank=False, unique=True, default=None)
    description = models.CharField(max_length=300, null=True, blank=True, default="")

    created = models.DateTimeField(editable=False, default=timezone.now, null=True, blank=True)
    modified = models.DateTimeField(default=timezone.now, null=True, blank=True)

    # Don't like this related name but we already used .klasses
    group = models.ForeignKey('groups.Group', related_name='klasses', null=True, blank=True, on_delete=models.PROTECT)

    image = models.ImageField(null=True, blank=True, upload_to=upload_image)
    syllabus = models.FileField(null=True, blank=True, upload_to=upload_syllabus)

    active = models.BooleanField(default=False)

    # status = models.CharField(max_length=60,)

    def __str__(self):
        return "{0} by {1}".format(self.course_number, self.instructor.user.username)

    @property
    def status(self):
        return "NOT-IMPLEMENTED"

    def create_copy(self):
        new_klass = Klass()
        # self.pk = None
        new_klass.instructor = self.instructor
        new_klass.title = self.title
        new_klass.description = self.description
        if self.image:
            print("we have an image")
            new_klass.image = ContentFile(self.image.read())
        if self.syllabus:
            print("We have a syllabus")
            new_klass.syllabus = ContentFile(self.syllabus.read())
        new_klass.group = self.group

        # new_klass.created = timezone.now()
        # new_klass.modified = timezone.now()
        new_klass.course_number = self.course_number + "_{}".format(str(uuid.uuid4())[0:5])
        # new_klass = self.save()
        new_klass.save()
        return new_klass
        # return new_klass

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)
