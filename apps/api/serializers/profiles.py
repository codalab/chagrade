from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from apps.profiles.models import Instructor, StudentMembership, AssistantMembership


User = get_user_model()


class InstructorSerializer(ModelSerializer):
    class Meta:
        model = Instructor
        fields = (
            'university_name',
        )


class ChaUserSerializer(ModelSerializer):

    instructor = InstructorSerializer()

    class Meta:
        model = User
        fields = (
            'username',
            # 'name',
            # 'email',
            # 'bio',
            'id',
            'instructor'
        )


class StudentMembershipSerializer(ModelSerializer):

    user = ChaUserSerializer()

    class Meta:
        model = StudentMembership
        fields = (
            # 'user',
            'klass',
            'student_id',
            'overall_grade',
            'date_enrolled',
        )
