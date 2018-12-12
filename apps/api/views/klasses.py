from django.contrib.auth import get_user_model
# from rest_framework.generics import GenericAPIView, RetrieveAPIView
# from rest_framework import permissions
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

# from apps.api.serializers.profiles import ChaUserSerializer

from apps.api import serializers
from apps.api.mixins import OwnerPermissionCheckMixin
from apps.api.permissions import KlassPermissionCheck

from apps.profiles.models import ChaUser
from apps.api.serializers.klasses import KlassSerializer

from apps.klasses.models import Klass

User = get_user_model()


class KlassViewSet(ModelViewSet):
    """Updating and inserting competitions are done by Producers."""
    queryset = Klass.objects.all()
    serializer_class = KlassSerializer
    permission_classes = (KlassPermissionCheck,)
