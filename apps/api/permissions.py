from rest_framework import permissions


class ChagradeAuthCheckMixin(object):

    def has_permission(self, request, view):
        return request.user.is_authenticated


class UserPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests"""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class StudentPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, and
     allow users who match the student and teacher to make changes."""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user == obj.user or request.user == obj.klass.instructor.user


class KlassPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow instructors, and only allow klass instructors (creators) to modify"""
    message = 'You are not allowed to use this resource.'

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
    message = 'You are not allowed to use this resource.'

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
    message = 'You are not allowed to use this resource.'

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
    message = 'You are not allowed to use this resource.'

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
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user == obj.creator.user


class GradePermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow the submission creator to modify. Anyone that's authenticated in a class can make a submission?"""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user == obj.evaluator.user


class TeamPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow the submission creator to modify. Anyone that's authenticated in a class can make a submission?"""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.instructor == obj.klass.instructor
