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


class KlassViewSet(OwnerPermissionCheckMixin, ModelViewSet):
    # """Updating and inserting competitions are done by Producers.
    #
    # request.user = Producer in this case."""
    queryset = Klass.objects.all()
    serializer_class = KlassSerializer
    # authentication_classes = ()
    permission_classes = ()

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     # context['producer'] = self.request.user
    #     return context

    # def get_queryset(self):
    #     qs = ChaUser.objects.all()
    #     # qs = qs.prefetch_related('phases', 'producer', 'admins', 'participants')
    #     return qs

    # def create(self, request, *args, **kwargs):
    #     """Overriding this for the following reasons:
    #
    #     1. Returning the huge amount of HTML/etc. back by default by DRF was bad
    #     2. We want to handle creating many competitions this way, and we do that
    #        custom to make drf-writable-nested able to interpret everything easily"""
    #     # Make the serializer take many competitions at once
    #     for competition in request.data:
    #         serializer = self.get_serializer(data=competition)
    #         serializer.is_valid(raise_exception=True)
    #         self.perform_create(serializer)
    #     return Response({}, status=status.HTTP_201_CREATED)
