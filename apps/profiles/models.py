import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?
from django.urls import reverse


class ChaUser(AbstractUser):
    email = models.EmailField(blank=True, unique=True, verbose_name='email address')
    instructor = models.OneToOneField('Instructor', related_name='user', null=True, blank=True, on_delete=models.CASCADE)

    has_set_password = models.BooleanField(default=False, null=False, blank=False)
    github_info = models.OneToOneField('GithubUserInfo', related_name='user', null=True, blank=True, on_delete=models.CASCADE)

    receive_emails_from_team = models.BooleanField(default=True)
    receive_emails_from_instructor = models.BooleanField(default=True)
    receive_emails_from_admins = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def is_instructor(self):
        return True if self.instructor else False


class Instructor(models.Model):
    university_name = models.CharField(max_length=200, null=True, blank=True)

    group = models.ForeignKey('groups.Group', related_name='instructor_members', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return "{0}".format(self.user.username)


class StudentMembership(models.Model):
    user = models.ForeignKey('ChaUser', related_name='klass_memberships', null=False, blank=False, on_delete=models.CASCADE)
    klass = models.ForeignKey('klasses.Klass', related_name='enrolled_students', null=False, blank=False, on_delete=models.CASCADE)
    team = models.ForeignKey('groups.Team', related_name='members', null=True, blank=True, on_delete=models.SET_NULL)

    student_id = models.CharField(null=False, blank=False, max_length=25)

    # This might need to be a property/method as it's calculated not stored
    overall_grade = models.FloatField(null=True, blank=True)

    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'klass')

    def __str__(self):
        return "{0}:{1} - {2}".format(self.user.username, self.student_id, self.klass.title)


class AssistantMembership(models.Model):
    instructor = models.ForeignKey('Instructor', related_name='assistant_memberships', null=False, blank=False, on_delete=models.CASCADE)
    klass = models.ForeignKey('klasses.Klass', related_name='assistants', null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return "{0} - {1}".format(self.instructor.user.username, self.klass.title)


class PasswordResetRequest(models.Model):
    user = models.ForeignKey('ChaUser', related_name='password_reset_requests', null=True, blank=True, on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4)

    @property
    def reset_link(self):
        return '{0}{1}'.format(settings.SITE_DOMAIN, reverse('profiles:reset_password_by_email', kwargs={'reset_key': self.key}))


class GithubUserInfo(models.Model):
    # Required Info
    uid = models.CharField(max_length=30, unique=True)

    # Misc/Avatar/Profile
    login = models.CharField(max_length=100, null=True, blank=True)  # username
    avatar_url = models.URLField(max_length=100, null=True, blank=True)
    gravatar_id = models.CharField(max_length=100, null=True, blank=True)
    html_url = models.URLField(max_length=100, null=True, blank=True)  # Profile URL
    name = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(max_length=2000, null=True, blank=True)
    location = models.CharField(max_length=120, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    # API Info
    node_id = models.CharField(unique=True, max_length=50, default='')
    url = models.URLField(max_length=100, null=True, blank=True)  # Base API URL
    followers_url = models.URLField(max_length=100, null=True, blank=True)
    following_url = models.URLField(max_length=100, null=True, blank=True)
    gists_url = models.URLField(max_length=100, null=True, blank=True)
    starred_url = models.URLField(max_length=100, null=True, blank=True)
    subscriptions_url = models.URLField(max_length=100, null=True, blank=True)
    organizations_url = models.URLField(max_length=100, null=True, blank=True)
    repos_url = models.URLField(max_length=100, null=True, blank=True)
    events_url = models.URLField(max_length=100, null=True, blank=True)
    received_events_url = models.URLField(max_length=100, null=True, blank=True)
