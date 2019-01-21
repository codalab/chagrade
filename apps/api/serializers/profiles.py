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
    student_id = serializers.CharField(max_length=200, required=False, allow_blank=True)
    klass = serializers.IntegerField(required=True)

    def create(self, validated_data):
        klass = Klass.objects.get(pk=validated_data.get('klass'))
        try:
            user = ChaUser.objects.get(email=validated_data.get('email'))
        except ObjectDoesNotExist:
            user = ChaUser.objects.create(email=validated_data.get('email'))
        try:
            student = StudentMembership.objects.get(user=user, klass=klass)
            return student
        except ObjectDoesNotExist:
            if not validated_data.get('student_id'):
                student_id = user.email.split('@')[0]
            else:
                student_id = validated_data.get('student_id')
            student = StudentMembership.objects.create(user=user, klass=klass, student_id=student_id)
            return student
