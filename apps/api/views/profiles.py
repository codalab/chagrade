import csv
import uuid

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
# from apps.api.serializers.profiles import ChaUserSerializer, StudentCreationSerializer, TestStudentSerializer
from apps.api.serializers.profiles import ChaUserSerializer, TestStudentSerializer

from apps.api import serializers
from apps.groups.models import Team
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


# def _check_username(username):
#     try:
#         ChaUser.objects.get(username=username)
#         new_username = username + str(uuid.uuid4())[0:4]
#         return self._check_username(new_username)
#     except ObjectDoesNotExist:
#         return username
#
#
# def _return_response(data, response_status_obj):
#     return Response(data, status=response_status_obj)


# @api_view(['POST'])
# def create_student(request, version):
#     # new_student_serializer = StudentCreationSerializer(data=request.data)
#     # new_student_serializer.is_valid(raise_exception=True)
#
#     print("!!!!!!!!!!!!!!")
#     print(request.data)
#     print("!!!!!!!!!!!!!!")
#
#     update_user = False
#     update_student = False
#
#     # Make sure we have an email and a klass at least
#
#     if not request.data.get('user') or not request.data.get('klass'):
#         return _return_response(
#             {'error': 'You need to pass user information, and a klass'},
#             status.HTTP_400_BAD_REQUEST
#         )
#     if not request.data['user'].get('email'):
#         return _return_response(
#             {'error': 'No email passed'},
#             status.HTTP_400_BAD_REQUEST
#         )
#
#     try:
#         klass = Klass.objects.get(pk=request.data.get('klass'))
#     except ObjectDoesNotExist:
#         return _return_response(
#             {'error': 'Could not find class!'},
#             status.HTTP_400_BAD_REQUEST
#         )
#
#     user_data = {
#         'email': request.data['user']['email'],
#         'first_name': request.data.get('first_name', ''),
#         'last_name': request.data.get('last_name', ''),
#     }
#
#     try:
#         user = User.objects.get(email=request.data['user']['email'])
#         update_user = True
#         user_data['id'] = user.pk
#     except ObjectDoesNotExist:
#         user = None
#         user_data['email'] = request.data['user']['email'],
#
#     if not request.data['user'].get('username'):
#         # If we did not pass a username, use our email split.
#         username = _check_username(user_data['email'].split('@')[0])
#     else:
#         print("@@@@@@@@@@@@")
#         print(request.data['user']['username'])
#         print(request.data.get('team'))
#         print("@@@@@@@@@@@@")
#         # If we passed a username, check that it's available (And if not generate one))
#         username = _check_username(request.data['user']['username'])
#
#     user_data['username'] = username
#
#     if not request.data.get('student_id'):
#         student_id = username
#     else:
#         student_id = request.data.get('student_id')
#
#     student_data = {
#         'user': user_data,
#         'student_id': student_id,
#         'klass': klass.pk,
#
#     }
#
#     if user:
#         try:
#             student = StudentMembership.objects.get(user=user, klass=klass)
#             update_student = True
#             student_data['id'] = student.pk
#         except ObjectDoesNotExist:
#             student = None
#     else:
#         student = None
#         # update_student = False
#
#     if request.data.get('team'):
#         student_data['team'] = request.data.get('team')
#         try:
#             team = Team.objects.get(klass=klass, name=request.data.get('team'))
#             # student_data['team'] = {
#             #     'klass': klass.pk,
#             #     'name': team.name,
#             #     'description': team.description,
#             #     'id': team.pk,
#             # }
#             # student_data['team'] = request.data.get('team')
#             student_data['team']['id'] = team.pk
#         except ObjectDoesNotExist:
#             team = None
#
#     print(student_data)
#     print(update_student)
#     print(update_user)
#
#
#
#
#     # if request.data.get('user'):
#     #     if request.data['user'].get('email'):
#     #         email = request.data['user']['email']
#     #     else:
#     #         _return_response(
#     #             {'error': 'No email passed'},
#     #             status.HTTP_400_BAD_REQUEST
#     #         )
#     # else:
#     #     _return_response(
#     #         {'error': 'No email passed'},
#     #         status.HTTP_400_BAD_REQUEST
#     #     )
#     #
#     #
#     # try:
#     #     klass = Klass.objects.get(pk=request.data.get('klass'))
#     # except ObjectDoesNotExist:
#     #     _return_response(
#     #         {'error': 'Class not found!'},
#     #         status.HTTP_400_BAD_REQUEST
#     #     )
#     #
#     # try:
#     #     user = User.objects.get(email=email)
#     #     data['user'] = {
#     #         'id': user.pk
#     #     }
#     # except ObjectDoesNotExist:
#     #     user = None
#     #     if request.data.get('user'):
#     #         data['user'] = {
#     #
#     #         }
#
#     # data = {
#     #     # "user": {
#     #     #     "username": username,
#     #     #     "first_name": request.data.get('user', {}).get('first_name'),
#     #     #     "last_name": request.data.get('user', {}).get('last_name'),
#     #     #     "email": email
#     #     # },
#     #     "klass": klass.pk,
#     #     # "student_id": student_id,
#     #     # "team": {
#     #     # "name": team.name,
#     #     # "description": "",
#     #     # "klass": klass.pk
#     #     # }
#     # }
#     #
#     # try:
#     #     user = User.objects.get(email=email)
#     #     data['user'] = {
#     #         'id': user.pk
#     #     }
#     # except ObjectDoesNotExist:
#     #     user = None
#     #     if request.data.get('user'):
#     #         data['user'] = {
#     #
#     #         }
#
#     # try:
#     #     student = StudentMembership.objects.get(klass=klass, user=user)
#     # except ObjectDoesNotExist:
#     #     student = None
#     #
#     #
#     # if request.data.get('team'):
#     #     try:
#     #         team = Team.objects.get(klass=klass, name=request.data['team'].get('name'))
#     #     except ObjectDoesNotExist:
#     #         team = Team.objects.create(klass=klass, name=request.data['team'].get('name'))
#     #
#     # username = _check_username(email.split('@')[0]) if not request.data.get('user').get('username') else _check_username(request.data.get('user').get('username'))
#     # student_id = username if not request.data.get('student_id') else request.data.get('student_id')
#
#     # data = {
#     #     "user": {
#     #         "username": username,
#     #         "first_name": request.data.get('user', {}).get('first_name'),
#     #         "last_name": request.data.get('user', {}).get('last_name'),
#     #         "email": email
#     #     },
#     #     "klass": klass.pk,
#     #     "student_id": student_id,
#     #     # "team": {
#     #         # "name": team.name,
#     #         # "description": "",
#     #         # "klass": klass.pk
#     #     # }
#     # }
#
#     # if team:
#     #     data['team']['id'] = team.pk
#     #     data['team']['name'] = team.name
#     #     data['team']['description'] = team.description
#     #
#     # if student:
#     #     data['id'] = student.pk
#     #     is_update = True
#     #
#     # if user:
#     #     data['user']['id'] = user.pk
#
#     # username if not validated_data.get('student_id') else validated_data.get('student_id')
#     #
#     # klass = Klass.objects.get(pk=validated_data.get('klass'))
#     # email = validated_data.get('email')
#     # If we weren't given a username, create a unique one from splitting the supplied email at the @ symbol
#     # username = self._check_username(email.split('@')[0]) if not validated_data.get(
#     #     'username') else self._check_username(validated_data.get('username'))
#     # user_dict = {
#     #     'email': email,
#     #     'username': username,
#     #     'first_name': validated_data.get('first_name', ''),
#     #     'last_name': validated_data.get('last_name', '')
#     # }
#     # user = self._get_or_create_user(user_dict)
#     # stud_dict = {
#     #     'user': user,
#     #     'klass': klass,
#     #     'student_id': username if not validated_data.get('student_id') else validated_data.get('student_id'),
#     # }
#     # if validated_data.get('team'):
#     #     try:
#     #         team = Team.objects.get(name=validated_data.get('team'), klass=klass)
#     #         stud_dict['team'] = team
#     #     except ObjectDoesNotExist:
#     #         # print(f"Could not find a team with id {validated_data.get('team')}")
#     #         team = Team.objects.create(name=validated_data.get('team'), klass=klass)
#     #         stud_dict['team'] = team
#     # stud = self._get_or_create_student(stud_dict)
#
#     # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
#     # print(f"Request.data is {request.data}")
#     # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
#
#     student_serializer = TestStudentSerializer(data=student_data)
#     student_serializer.is_valid(raise_exception=True)
#
#     if student_serializer.errors:
#         return Response({'errors': student_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         if update_student:
#             # student_serializer.create(student_serializer.validated_data)
#             student_serializer.save()
#             #student = student_serializer.update(student, student_serializer.validated_data)
#         else:
#             new_student = student_serializer.create(student_serializer.validated_data)
#             new_student.user.set_password(new_student.username)
#             new_student.user.save()
#         return Response({'response': 'success'}, status=status.HTTP_201_CREATED)
#
#     # Student or klass does not exist?
#     # Try to create student
#     # if new_student_serializer.errors:
#     #     return Response({'errors': new_student_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
#     # else:
#     #     new_student_serializer.create(new_student_serializer.validated_data)
#     #     return Response({'response': 'success'}, status=status.HTTP_201_CREATED)
#
#
class TestStudentViewSet(ModelViewSet):
    queryset = StudentMembership.objects.all()
    serializer_class = serializers.profiles.TestStudentSerializer

    # def create(self, request, *args, **kwargs):
    #     print(type(request.data))
    #     team_name = request.data.pop('team', None)
    #     if team_name:
    #         try:
    #             team = Team.objects.get(name=team_name, klass=request.data.get('klass'))
    #             request.data['team'] = team.pk
    #         except ObjectDoesNotExist:
    #             print(f"Failed to find team: {team_name}")
    #     super().create(request, *args, **kwargs)

@api_view(['POST'])
def create_students_from_csv(request, version):
    print(request.data)
    # klass = Klass.objects.get(pk=request.data.get('klass'))
    with open(request.FILES['file'].temporary_file_path()) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print("First row")
                # line_count += 1
            else:
                if len(row) >= 6:
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
                    print("@@@DIX@@@")
                    print(data)
                    # new_student_serializer = StudentCreationSerializer(data=data)
                    new_student_serializer = TestStudentSerializer(data=data)
                    new_student_serializer.is_valid(raise_exception=True)
                    if new_student_serializer.errors:
                        return Response({'errors': new_student_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        new_student_serializer.save()
                        # new_student_serializer.save(**new_student_serializer.validated_data)
                else:
                    print("Row too short to read.")
            line_count += 1
        print('Processed {} lines.'.format(line_count))
    return Response({'response': 'success'})
