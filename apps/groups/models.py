from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?


class Group(models.Model):
    creator = models.ForeignKey('profiles.Instructor', related_name='created_groups', null=False, blank=False, on_delete=models.CASCADE)

    template = models.ForeignKey('klasses.Klass', related_name='group_template', null=True, blank=True, on_delete=models.PROTECT)

    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)


class Team(models.Model):
    klass = models.ForeignKey('klasses.Klass', related_name='teams', null=True, blank=True, on_delete=models.PROTECT)
    # members = models.ManyToManyField('profiles.ChaUser', through='KlassTeamMembership')

    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)
