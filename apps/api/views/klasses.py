from django.contrib.auth import get_user_model
# from rest_framework.generics import GenericAPIView, RetrieveAPIView
# from rest_framework import permissions
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet, ModelViewSet

# from apps.api.serializers.profiles import ChaUserSerializer

from apps.api import serializers
from apps.api.mixins import OwnerPermissionCheckMixin

from apps.profiles.models import ChaUser
from apps.api.serializers.klasses import KlassSerializer

from apps.klasses.models import Klass

User = get_user_model()


# class GetMyProfile(RetrieveAPIView, GenericAPIView):
#     # queryset = User.objects.all()
#     serializer_class = ChaUserSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_object(self):
#         return self.request.user


class KlassViewSet(ModelViewSet):
    """Updating and inserting competitions are done by Producers."""
    queryset = Klass.objects.all()
    serializer_class = KlassSerializer
    permission_classes = ()
