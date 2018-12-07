from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from apps.api.serializers.homework import SubmissionSerializer
from apps.groups.models import Team
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
            # 'user',
            'klass',
            'student_id',
            'overall_grade',
            'date_enrolled',
        )


class BasicTeamSerializer(ModelSerializer):

    class Meta:
        model = Team
        fields = [
            'name',
            'description',
        ]


class DetailedStudentSerializer(ModelSerializer):

    user = ChaUserSerializer()
    team = BasicTeamSerializer()
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
