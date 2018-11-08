from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from apps.profiles.models import Instructor, StudentMembership

# from apps.api.serializers.klasses import KlassSerializer


User = get_user_model()


class ChaUserSerializer(ModelSerializer):
    # instructor = InstructorSerializer()

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'first_name',
            'last_name',
            'email',
            # 'instructor',
            # 'student',
        )


class StudentSerializer(ModelSerializer):

    # user = ChaUserSerializer()

    class Meta:
        model = StudentMembership
        fields = (
            'user',
            'klass',
            'student_id',
            'overall_grade',
            'date_enrolled',
        )


class DetailedStudentSerializer(ModelSerializer):

    user = ChaUserSerializer()

    class Meta:
        model = StudentMembership
        fields = (
            'user',
            'klass',
            'student_id',
            'overall_grade',
            'date_enrolled',
        )
