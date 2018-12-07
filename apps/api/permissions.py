# from rest_framework import permissions

# from producers.models import Producer


# class ProducerPermission(permissions.BasePermission):
#     message = 'Only producers may modify ChaHub information.'
#
#     def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         else:
#             # The ProducerAuthentication class sets request.user to Producer,
#             # TODO: Check object permissions, should only be able to work on non existant objects or
#             # objects where producer == producer!!!
#             return isinstance(request.user, Producer)
from rest_framework import permissions


class CheckKlassInstructor(permissions.BasePermission):
    message = 'Only class instructors can modify classes.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user == obj.instructor:
            return True
        else:
            return False


class CheckObjKlassInstructor(permissions.BasePermission):
    message = 'Only class instructors can modify classes.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user == obj.klass.instructor:
            return True
        else:
            return False


class CheckObjDefinitionKlassInstructor(permissions.BasePermission):
    message = 'Only class instructors can modify classes.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user == obj.definition.klass.instructor:
            return True
        else:
            return False


class CheckSubmissionOwner(permissions.BasePermission):
    message = 'Only class instructors can modify classes.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user == obj.creator:
            return True
        else:
            return False


class CheckSubmissionKlassInstructor(permissions.BasePermission):
    message = 'Only class instructors can modify classes.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        if request.user == obj.submission.klass.instructor:
            return True
        else:
            return False
