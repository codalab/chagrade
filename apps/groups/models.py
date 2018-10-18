from django.db import models

# Require an account type to determine users vs students?
# Or should we abstract two seperate sub-models from this one?


class InstructorGroup(models.Model):
    creator = models.ForeignKey('profiles.Instructor', related_name='created_groups', null=False, blank=False, on_delete=models.CASCADE)
    members = models.ManyToManyField('profiles.Instructor', through='InstructorGroupMembership')

    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)


class KlassTeam(models.Model):
    klass = models.ForeignKey('klasses.Klass', related_name='teams', null=True, blank=True, on_delete=models.PROTECT)
    members = models.ManyToManyField('profiles.ChaUser', through='KlassTeamMembership')

    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.CharField(max_length=200, null=True, blank=True)


class InstructorGroupMembership(models.Model):
    instructor = models.ForeignKey('profiles.Instructor', related_name='group_memberships', null=False, blank=False, on_delete=models.PROTECT)
    group = models.ForeignKey('InstructorGroup', null=False, blank=False, on_delete=models.PROTECT)


class KlassTeamMembership(models.Model):
    user = models.ForeignKey('profiles.ChaUser', related_name='klass_team_memberships', null=False, blank=False, on_delete=models.PROTECT)
    team = models.ForeignKey('KlassTeam', null=False, blank=False, on_delete=models.PROTECT)