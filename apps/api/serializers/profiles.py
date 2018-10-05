from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from apps.profiles.models import Instructor, StudentMembership

# from apps.api.serializers.klasses import KlassSerializer


User = get_user_model()


class BasicChaUserSerializer(ModelSerializer):
    # from apps.api.serializers.profiles import InstructorSerializer

    # instructor = InstructorSerializer()

    class Meta:
        model = User
        fields = (
            'username',
            'id',
        )


class InstructorSerializer(ModelSerializer):

    # user = BasicChaUserSerializer()

    class Meta:
        model = Instructor
        fields = (
            'university_name',
            # 'user'
        )


class ChaUserSerializer(ModelSerializer):
    instructor = InstructorSerializer()

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'instructor',
            'student',
        )


class StudentMembershipSerializer(ModelSerializer):

    user = ChaUserSerializer()
    # klass = KlassSerializer()

    class Meta:
        model = StudentMembership
        fields = (
            # 'klass',
            # 'student_id',
            'overall_grade',
            'date_enrolled',
        )
