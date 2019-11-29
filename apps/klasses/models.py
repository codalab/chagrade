import uuid

from django.core.files.base import ContentFile
from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?


# models.PROTECT says to forbid the deletion of the referenced object. To delete it we ahve to manually delete all
# references.
from django.utils import timezone

from apps.homework.models import Submission, Grade


def upload_image(instance, filename):
    file_split = filename.split('.')
    file_extension = file_split[len(file_split) - 1]
    path = f'images/{instance.pk}/{instance.course_number}/class_image.{file_extension}'
    return path


def upload_syllabus(instance, filename):
    file_split = filename.split('.')
    file_extension = file_split[len(file_split) - 1]
    path = f'syllabi/{instance.pk}/{instance.course_number}/class_syllabus.{file_extension}'
    return path


class Klass(models.Model):
    # COMPLETE = 'complete'
    # INCOMPLETE = 'incomplete'

    instructor = models.ForeignKey('profiles.Instructor', related_name='klasses', on_delete=models.CASCADE)

    title = models.CharField(max_length=60, null=False, blank=False, default="New Course")
    course_number = models.SlugField(max_length=60, null=False, blank=False)
    description = models.CharField(max_length=300, null=True, blank=True, default="")

    created = models.DateTimeField(editable=False, default=timezone.now, null=True, blank=True)
    modified = models.DateTimeField(default=timezone.now, null=True, blank=True)

    # Don't like this related name but we already used .klasses
    group = models.ForeignKey('groups.Group', related_name='klasses', null=True, blank=True, on_delete=models.SET_NULL)

    image = models.ImageField(null=True, blank=True, upload_to=upload_image)
    syllabus = models.FileField(null=True, blank=True, upload_to=upload_syllabus)

    active = models.BooleanField(default=False)

    def __str__(self):
        return "{0} by {1}".format(self.course_number, self.instructor.user.username)

    @property
    def status(self):
        return "NOT-IMPLEMENTED"

    def create_copy(self):
        new_klass = Klass()
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

        new_klass.course_number = self.course_number
        new_klass.save()
        return new_klass

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super().save(*args, **kwargs)

    def homeworks_completely_graded(self):
        for hw in self.homework_definitions.all():
            if hw.team_based:
                for team in self.teams.all():
                    team_graded = False
                    submissions = Submission.objects.filter(team=team, definition=hw)
                    for submission in submissions:
                        if Grade.objects.filter(submission=submission, published=False):
                            return False
                        if Grade.objects.filter(submission=submission, published=True):
                            team_graded = True
                            break
                    if not submissions:
                        team_graded = True
                    if not team_graded:
                        return False
                return True

            else:
                for student in self.enrolled_students.all():
                    student_graded = False
                    submissions = Submission.objects.filter(creator=student, definition=hw)
                    for submission in submissions:
                        if Grade.objects.filter(submission=submission, published=False):
                            return False
                        if Grade.objects.filter(submission=submission, published=True):
                            student_graded = True
                            break
                    if not submissions:
                        student_graded = True
                    if not student_graded:
                        return False
                return True
