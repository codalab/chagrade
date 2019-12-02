import csv

from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework import permissions, status
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.api.permissions import StudentPermissionCheck, UserPermissionCheck
from apps.api.serializers.profiles import ChaUserSerializer, TestStudentSerializer

from apps.api import serializers

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


class TestStudentViewSet(ModelViewSet):
    queryset = StudentMembership.objects.all()
    serializer_class = serializers.profiles.TestStudentSerializer


@api_view(['POST'])
def create_students_from_csv(request, version):
    with open(request.FILES['file'].temporary_file_path()) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if len(row) >= 6:
                if row[0] == 'First Name' and row[3] == 'Student ID' and row[4] == 'Student Email':
                    continue
                data = {
                    'user': {
                        'first_name': row[0],
                        'last_name': row[1],
                        'username': row[2],
                        'email': row[4],
                    },
                    'student_id': row[3],
                    'team': {
                        'name': row[5],
                        'klass': request.data.get('klass')
                    },
                    'klass': request.data.get('klass'),
                }
                new_student_serializer = TestStudentSerializer(data=data)
                new_student_serializer.is_valid(raise_exception=True)
                if new_student_serializer.errors:
                    return Response({'errors': new_student_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    new_student = new_student_serializer.save()
                    # If there's something in the student leader column
                    if len(row) == 7:
                        new_student.team.leader = new_student
                        new_student.team.save()
            else:
                print("Row too short to read.")
            line_count += 1
        print('Processed {} lines.'.format(line_count))
    return Response({'response': 'success'})
