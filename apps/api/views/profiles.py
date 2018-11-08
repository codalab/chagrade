from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework import permissions, status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.api.serializers.profiles import ChaUserSerializer

from apps.api import serializers
from apps.klasses.models import Klass

from apps.profiles.models import ChaUser, StudentMembership

User = get_user_model()


class GetMyProfile(RetrieveAPIView, GenericAPIView):
    # queryset = User.objects.all()
    serializer_class = ChaUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ProfileViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin, GenericViewSet):
    # """Updating and inserting competitions are done by Producers.
    #
    # request.user = Producer in this case."""
    queryset = ChaUser.objects.all()
    serializer_class = serializers.profiles.ChaUserSerializer
    authentication_classes = ()
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


class StudentViewSet(ModelViewSet):
    queryset = StudentMembership.objects.all()
    serializer_class = serializers.profiles.DetailedStudentSerializer
    permission_classes = ()

    def get_queryset(self):
        print("Getting queryset")
        queryset = self.queryset
        klass_pk = self.request.query_params.get('klass_pk', None)
        print(self.request.query_params)
        print(klass_pk)
        if klass_pk is not None:
            try:
                klass = Klass.objects.get(pk=klass_pk)
                if self.request.user != klass.instructor.user:
                    raise Http404("User not allowed!")
                queryset = queryset.filter(klass=klass)
            except ObjectDoesNotExist:
                raise Http404("Klass object with pk: {} not found!".format(klass_pk))
        return queryset

    def create(self, request, *args, **kwargs):

        # We need the simple serializer to only pass a user PK
        self.serializer_class = serializers.profiles.StudentSerializer

        # super(StudentViewSet, self).create(request, *args, **kwargs)
        # Augment the default behavior to return the secret key instead of the entire producer object

        # We then display the API key to the user to forward on to the producer

        data = request.data

        print(data)

        # Get our user if we don't pass data['user']
        # If we don't pass data['user'] then try to get data['user_name'] and pop it out
        # We should send klass from the form, but we should double check perms here
        # if not data.get('user'):
        #     print("No user")
        if data.get('user_name') and data.get('user_email'):
            new_user, created = ChaUser.objects.get_or_create(username=data.pop('user_name'), email=data.pop('user_email'))
            if created:
                print("We created a new user!")
            else:
                print("We found an existing user!")

            if new_user:
                data['user'] = new_user.pk
            else:
                raise Http404("Could not create or find a user")

        else:
            if data.get('user_name'):
                print("We have a user_name")
                try:
                    if not data.get('user'):
                        data['user'] = ChaUser.objects.get(username=data.pop('user_name')).pk
                        print(data['user'])
                except ObjectDoesNotExist:
                    return Response({
                        'errors': {'user_name': 'User not found!'}
                    }, status=status.HTTP_404_NOT_FOUND)
                    # raise Http404("Could not attribute a user to new student.")

            # if not data.get('user'):
            if data.get('user_email'):
                print("We have an email")
                try:
                    if not data.get('user'):
                        data['user'] = ChaUser.objects.get(email=data.pop('user_email')).pk
                        print(data['user'])
                except ObjectDoesNotExist:
                    return Response({
                        'errors': {'user_email': 'User not found!'}
                    }, status=status.HTTP_404_NOT_FOUND)
                    # raise Http404("Could not attribute a user to new student.")

            print("Trying to get class")
            try:
                print(data.get('klass'))
                klass = Klass.objects.get(pk=data.get('klass'))
                if klass.instructor.user != request.user:
                    raise Http404("User not allowed to make a new student for this class!")
            except ObjectDoesNotExist:
                # raise Http404("Klass not found")
                return Response({
                    'errors': {'klass': 'Klass not found!'}
                }, status=status.HTTP_404_NOT_FOUND)

        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
