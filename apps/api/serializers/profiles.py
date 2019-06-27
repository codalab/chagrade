from django.contrib.auth import get_user_model
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from apps.api.serializers.homework import SubmissionSerializer
from apps.api.utils import get_unique_username
from apps.groups.models import Team
from apps.profiles.models import StudentMembership, ChaUser

User = get_user_model()


class ChaUserSerializer(WritableNestedModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'first_name',
            'last_name',
            'email',
            'github_repos'
        )
        extra_kwargs = {
            'username': {'validators': [], 'required': False, 'allow_blank': True},
            'email': {'validators': []},
            'github_repos': {'read_only': True}
        }

    def validate(self, attrs):
        if 'username' not in attrs or not attrs['username']:
            username = attrs['email'].split("@")[0]
        else:
            username = attrs['username']
        attrs['username'] = get_unique_username(username, attrs['email'])
        return attrs

    def create(self, validated_data):
        try:
            user = ChaUser.objects.get(email=validated_data['email'])
            return super().update(user, validated_data)
        except ChaUser.DoesNotExist:
            # When we create a new user, set their password
            # return super().create(validated_data)
            new_user = super().create(validated_data)
            new_user.set_password(validated_data['email'].split('@')[0])
            new_user.save()
            return new_user


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentMembership
        fields = (
            'klass',
            'student_id',
            'overall_grade',
            'date_enrolled',
            'id',
        )


class BasicTeamSerializer(WritableNestedModelSerializer):

    class Meta:
        model = Team
        fields = [
            'name',
            'description',
            'klass',
            'id'
        ]
        extra_kwargs = {
            'name': {'validators': [], 'allow_blank': True},
            # 'name': {'validators': []},
        }

    def get_unique_together_validators(self):
        '''
        Overriding method to disable unique together checks
        '''
        return []

    def create(self, validated_data):
        try:
            team = Team.objects.get(klass=validated_data['klass'], name=validated_data['name'])
            return super().update(team, validated_data)
        except Team.DoesNotExist:
            return super().create(validated_data)


class DetailedStudentSerializer(WritableNestedModelSerializer):

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


class TestStudentSerializer(WritableNestedModelSerializer):
    user = ChaUserSerializer(required=True)
    team = BasicTeamSerializer(required=False, allow_null=True)

    class Meta:
        model = StudentMembership
        fields = (
            'user',
            'klass',
            'student_id',
            'id',
            'team',
        )
        extra_kwargs = {
            #'team': {'validators': []},
            'student_id': {'validators': [], 'required': False, 'allow_blank': True},
        }

    def validate(self, attrs):
        if 'student_id' not in attrs or not attrs['student_id']:
            student_id = attrs['user']['email'].split("@")[0]
        else:
            student_id = attrs['student_id']
        attrs['student_id'] = get_unique_username(student_id, attrs['user']['email'])
        return attrs

    def create(self, validated_data):
        try:
            student = StudentMembership.objects.get(klass=validated_data.get('klass'), user__email=validated_data['user']['email'])
            return super().update(student, validated_data)
        except StudentMembership.DoesNotExist:
            return super().create(validated_data)
