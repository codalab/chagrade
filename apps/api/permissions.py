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
