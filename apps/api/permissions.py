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

#
# class CheckKlassInstructor(permissions.BasePermission):
#     message = 'Only class instructors can modify classes.'
#
#     def has_object_permission(self, request, view, obj):
#         if request.user.is_anonymous:
#             return False
#         if request.user == obj.instructor:
#             return True
#         else:
#             return False

# TODO: Determine if we really need to check if user is authenticated. Pretty sure DRF does this for us


class ChagradeAuthCheckMixin(object):

    def has_permission(self, request, view):
        print("were checking perms")
        if not request.user.is_authenticated or request.user.is_anonymous:
            print("!!!!!!!!!!!!!!!")
            # print(request.user)
            print(not request.user.is_authenticated)
            print(request.user.is_anonymous)
            print("!!!!!!!!")
            print("false")
            return False
        else:
            print("true")
            return True


class UserPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests"""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        print("CHECKING PERMISSIONS DOI")
        if request.method in permissions.SAFE_METHODS:
            print("Yep")
            return True
        else:
            print("Nope")
            return False


class StudentPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, and
     allow users who match the student and teacher to make changes."""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        print("!!!!!!!!!!!!")
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user == obj.user or request.user == obj.klass.instructor:
                return True
            else:
                return False


class KlassPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow instructors, and only allow klass instructors (creators) to modify"""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        # if not request.user or not request.user.is_authenticated or request.user.is_anonymous:
        #     return False
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if not request.user.instructor:
                return False
            else:
                if request.user.instructor == obj.instructor:
                    return True
                else:
                    return False


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
                if request.user.instructor == obj.klass.instructor:
                    return True
                else:
                    return False


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
                if request.user.instructor == obj.definition.klass.instructor:
                    return True
                else:
                    return False


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
                if request.user.instructor == obj.definition.klass.instructor:
                    return True
                else:
                    return False


class SubmissionPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow the submission creator to modify. Anyone that's authenticated in a class can make a submission?"""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user == obj.creator.user:
                return True
            else:
                return False


class GradePermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow the submission creator to modify. Anyone that's authenticated in a class can make a submission?"""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user == obj.evaluator:
                return True
            else:
                return False


class TeamPermissionCheck(ChagradeAuthCheckMixin, permissions.BasePermission):
    """Only allow authenticated users to make get requests, only
     allow the submission creator to modify. Anyone that's authenticated in a class can make a submission?"""
    message = 'You are not allowed to use this resource.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user.instructor == obj.klass.instructor:
                return True
            else:
                return False
