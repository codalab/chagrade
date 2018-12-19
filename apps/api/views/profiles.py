import csv

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework import permissions, status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.api.permissions import StudentPermissionCheck, UserPermissionCheck
from apps.api.serializers.profiles import ChaUserSerializer, StudentCreationSerializer

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


class ProfileViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = ChaUser.objects.all()
    serializer_class = serializers.profiles.ChaUserSerializer
    permission_classes = (UserPermissionCheck,)


class StudentViewSet(ModelViewSet):
    queryset = StudentMembership.objects.all()
    serializer_class = serializers.profiles.DetailedStudentSerializer
    permission_classes = (StudentPermissionCheck,)


@api_view(['POST'])
def create_student(request, version):
    new_student_serializer = StudentCreationSerializer(data=request.data)
    new_student_serializer.is_valid(raise_exception=True)
    if new_student_serializer.errors:
        return Response({'errors': new_student_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        new_student_serializer.create(new_student_serializer.validated_data)
        return Response({'response': 'success'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_students_from_csv(request, version):
    print(request.data)
    # klass = Klass.objects.get(pk=request.data.get('klass'))
    with open(request.FILES['file'].temporary_file_path()) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            line_count += 1
            if len(row) > 1:
                data = {
                    'email': row[0],
                    'klass': request.data.get('klass'),
                    'student_id': row[1]
                }
            else:
                data = {
                    'email': row[0],
                    'klass': request.data.get('klass')
                }

            new_student_serializer = StudentCreationSerializer(data=data)
            new_student_serializer.is_valid(raise_exception=True)
            if new_student_serializer.errors:
                return Response({'errors': new_student_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                new_student_serializer.create(new_student_serializer.validated_data)
        print('Processed {} lines.'.format(line_count))
    return Response({'response': 'success'})
