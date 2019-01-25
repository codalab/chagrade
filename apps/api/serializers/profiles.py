import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.api.serializers.homework import SubmissionSerializer
from apps.groups.models import Team
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership, ChaUser

# from apps.api.serializers.klasses import KlassSerializer


User = get_user_model()


class ChaUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'first_name',
            'last_name',
            'email',
        )


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentMembership
        fields = (
            'klass',
            'student_id',
            'overall_grade',
            'date_enrolled',
        )


class BasicTeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = [
            'name',
            'description',
        ]


class DetailedStudentSerializer(serializers.ModelSerializer):

    user = ChaUserSerializer()
    team = BasicTeamSerializer(required=False)
    submitted_homeworks = SubmissionSerializer(many=True)

    class Meta:
        model = StudentMembership
        fields = (
            'user',
            'klass',
            'student_id',
            'overall_grade',
            'date_enrolled',
            'id',
            'team',
            'submitted_homeworks'
        )


class StudentCreationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    klass = serializers.IntegerField(required=True)

    student_id = serializers.CharField(max_length=200, required=False, allow_blank=True)
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    team = serializers.IntegerField(required=False, allow_null=True, default=None)

    def _get_or_create_user(self, user_dict):
        try:
            user = ChaUser.objects.get(email=user_dict['email'])
            return user
        except ObjectDoesNotExist:
            user = ChaUser.objects.create(**user_dict)
            temp_password = user_dict['email'].split('@')[0]
            print(f"SETTING PASSWORD TO {temp_password}")
            user.set_password(temp_password)
            user.save()
            return user

    def _get_or_create_student(self, student_dict):
        try:
            stud = StudentMembership.objects.get(klass=student_dict['klass'], user=student_dict['user'])
            return stud
        except ObjectDoesNotExist:
            stud = StudentMembership.objects.create(**student_dict)
            return stud

    def _check_username(self, username):
        try:
            ChaUser.objects.get(username=username)
            new_username = username + str(uuid.uuid4())[0:4]
            return self._check_username(new_username)
        except ObjectDoesNotExist:
            return username

    def create(self, validated_data):
        try:
            klass = Klass.objects.get(pk=validated_data.get('klass'))
            email = validated_data.get('email')
            # If we weren't given a username, create a unique one from splitting the supplied email at the @ symbol
            username = self._check_username(email.split('@')[0]) if not validated_data.get('username') else self._check_username(validated_data.get('username'))
            user_dict = {
                'email': email,
                'username': username,
                'first_name': validated_data.get('first_name', ''),
                'last_name': validated_data.get('last_name', '')
            }
            user = self._get_or_create_user(user_dict)
            stud_dict = {
                'user': user,
                'klass': klass,
                'student_id': username if not validated_data.get('student_id') else validated_data.get('student_id'),
                # 'team__pk': None if not validated_data.get('team') else validated_data.get('team')
            }
            if validated_data.get('team'):
                try:
                    team = Team.objects.get(pk=validated_data.get('team'))
                    stud_dict['team'] = team
                except ObjectDoesNotExist:
                    print(f"Could not find a team with id {validated_data.get('team')}")
            stud = self._get_or_create_student(stud_dict)
            print("COMPLETED SUCCESFULLY")
            return stud

        except ObjectDoesNotExist:
            print("Could not find klass object for student!")
            return None
