import csv

from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework import permissions, status
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.exceptions import ValidationError, ErrorDetail

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


def make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix


@api_view(['POST'])
def create_students_from_csv(request, version):
    with open(request.FILES['file'].temporary_file_path()) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if len(row) >= 6:
                if row[3] == 'Student ID' and row[4] == 'Student Email':
                    continue
                data = {
                    'user': {
                        'first_name': row[0],
                        'last_name': row[1],
                        'username': row[2],
                        'email': row[4],
                    },
                    'student_id': row[3],
                    'klass': request.data.get('klass'),
                }

                contains_valid_team_name = any(character.isalpha() for character in row[5])

                if contains_valid_team_name:
                    data['team'] = {
                        'name': row[5],
                        'klass': request.data.get('klass')
                    }
                new_student_serializer = TestStudentSerializer(data=data)
                try:
                    new_student_serializer.is_valid(raise_exception=True)
                except ValidationError:
                    if new_student_serializer.errors:
                        error_dict = dict(new_student_serializer.errors)
                        error_dict['student'] = {'identifier': [ErrorDetail(f'From top of CSV, {make_ordinal(line_count + 1)} student with email: {str(row[4])}', code='invalid')]}
                        raise ValidationError(error_dict)

                new_student = new_student_serializer.save()
                # If there's something in the student leader column
                if len(row) == 7 and contains_valid_team_name and row[6] in ['t', 'T', 'true', 'True', 'TRUE']:
                    new_student.team.leader = new_student
                    new_student.team.save()
            else:
                print("Row too short to read.")
            line_count += 1
        print('Processed {} lines.'.format(line_count))
    return Response({'response': 'success'})
