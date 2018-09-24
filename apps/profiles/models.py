from django.contrib.auth.models import AbstractUser
from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?


class ChaUser(AbstractUser):
    # instructor_profile = models.ForeignKey('InstructorProfile', related_name='user', null=True, blank=True)
    instructor_profile = models.OneToOneField('Instructor', related_name='user', null=True, blank=True, on_delete=models.CASCADE)

    receive_emails_from_team = models.BooleanField(default=True)
    receive_emails_from_instructor = models.BooleanField(default=True)
    receive_emails_from_admins = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def is_instructor(self):
        return True if self.instructor_profile else False


class Instructor(models.Model):
    university_name = models.CharField(max_length=200, null=True, blank=True)


class StudentMembership(models.Model):
    user = models.ForeignKey('ChaUser', related_name='klass_memberships', null=False, blank=False, on_delete=models.CASCADE)
    klass = models.ForeignKey('klasses.Klass', related_name='enrolled_students', null=False, blank=False, on_delete=models.CASCADE)

    student_id = models.CharField(null=False, blank=False, max_length=25)

    # This might need to be a property/method as it's calculated not stored
    overall_grade = models.FloatField(null=True, blank=True)

    date_enrolled = models.DateTimeField(auto_now_add=True)


class AssistantMembership(models.Model):
    instructor = models.ForeignKey('Instructor', related_name='assistant_memberships', null=False, blank=False, on_delete=models.CASCADE)
    klass = models.ForeignKey('klasses.Klass', related_name='assigned_assistants', null=False, blank=False, on_delete=models.CASCADE)



