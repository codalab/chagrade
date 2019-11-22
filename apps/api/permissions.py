from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions

from apps.profiles.models import StudentMembership
from apps.klasses.models import Klass
from apps.groups.models import Team


class ChagradeAuthCheckMixin(object):

    def extra_permission_check(self, request):
        return True

    def has_permission(self, request, view):
        """Must be an authenticated user, and pass extra_permission_check (True by default)"""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        else:
            return request.user.is_authenticated and self.extra_permission_check(request)


class UserPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests"""
    message = 'You must be logged in to access Users.'

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class StudentPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, and
     allow users who match the student and teacher to make changes."""
    message = 'You must be logged in to access Students, or an instructor to make modifications to Students'

    def extra_permission_check(self, request):
        return request.user.instructor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user == obj.user or request.user == obj.klass.instructor.user


class KlassPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow instructors, and only allow klass instructors (creators) to modify"""
    message = 'You must be logged in to access Classes, or an instructor to make modifications to Classes'

    def extra_permission_check(self, request):
        return request.user.instructor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if not request.user.instructor:
                return False
            else:
                return request.user.instructor == obj.instructor


class DefinitionPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow instructors, and only allow klass instructors (creators) to modify"""
    message = 'You must be logged in to access Definitions, or an instructor to make modifications to Definitions'

    def extra_permission_check(self, request):
        return request.user.instructor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if not request.user.instructor:
                return False
            else:
                return request.user.instructor == obj.klass.instructor


class CriteriaPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow instructors, and only allow klass instructors (creators) to modify"""
    message = 'You must be logged in to access Criterias, or an instructor to make modifications to Criterias'

    def extra_permission_check(self, request):
        return request.user.instructor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if not request.user.instructor:
                return False
            else:
                return request.user.instructor == obj.definition.klass.instructor


class QuestionPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow instructors, and only allow klass instructors (creators) to modify"""
    message = 'You must be logged in to access Questions, or an instructor to make modifications to Questions'

    def extra_permission_check(self, request):
        return request.user.instructor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if not request.user.instructor:
                return False
            else:
                return request.user.instructor == obj.definition.klass.instructor


class SubmissionPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow the submission creator to modify. Anyone that's authenticated in a class can make a submission?"""
    message = 'You must be the submission creator, or in the same team to view submissions.'

    def has_object_permission(self, request, view, obj):
        try:
            student = StudentMembership.objects.get(klass=obj.definition.klass, user=request.user)
        except ObjectDoesNotExist:
            print("Error! Could not find matching student for user!")
            student = None
        # If we're a teacher attempting to get the submission, allow it, but not for modification/deleting
        if request.method in permissions.SAFE_METHODS and request.user.instructor:
            if request.user.instructor == obj.definition.klass.instructor:
                return True
        # If we're a student, and there's teams, allow students in the team, or the creator
        if student:
            if obj.team:
                if student in obj.team.members.all():
                    return True
            if student == obj.creator:
                return True
        return False


class GradePermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow the submission creator to modify. Anyone that's authenticated in a class can make a submission?"""
    message = 'You must be logged in to access Grades, or an instructor to make modifications to Grades'

    def extra_permission_check(self, request):
        return request.user.instructor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user == obj.evaluator.user


class TeamPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow the submission creator to modify. Anyone that's authenticated in a class can make a submission?"""
    message = 'You must be logged in to access Teams, or an instructor to make modifications to Teams'

    def extra_permission_check(self, request):
        return request.user.instructor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.instructor:
            return request.user.instructor == obj.klass.instructor
        else:
            return False


class CustomChallengeURLPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow the submission creator to modify. Anyone that's authenticated in a class can make a submission?"""
    message = 'You must be logged in to access ChallengeURLS, or an instructor to make modifications to Teams'

    def extra_permission_check(self, request):
        return request.user.instructor

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.instructor:
            return request.user.instructor == obj.definition.klass.instructor
        else:
            return False


class InstructorOrSuperuserPermission(permissions.BasePermission):
    message = 'You are not allowed to access this data.'

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        klass_pk = view.kwargs.get('klass_pk')
        student_pk = view.kwargs.get('student_pk')
        team_pk = view.kwargs.get('team_pk')

        instructor = None
        try:
            instructor = request.user.instructor
        except AttributeError:
            return False

        if klass_pk:
            klass = get_object_or_404(Klass, pk=klass_pk)
            if instructor == klass.instructor:
                return True

        elif student_pk:
            student = get_object_or_404(StudentMembership, pk=student_pk)
            if instructor == student.klass.instructor:
                return True

        elif team_pk:
            team = get_object_or_404(Team, pk=team_pk)
            if instructor == team.klass.instructor:
                return True
        return False
