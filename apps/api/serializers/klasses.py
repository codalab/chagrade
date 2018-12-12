from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from apps.api.serializers.groups import TeamSerializer
from apps.klasses.models import Klass
from apps.api.serializers.profiles import DetailedStudentSerializer


class KlassSerializer(ModelSerializer):
    # from apps.api.serializers.profiles import InstructorSerializer

    # instructor = InstructorSerializer()

    enrolled_students = DetailedStudentSerializer(many=True, required=False)
    teams = TeamSerializer(many=True, required=False)

    class Meta:
        model = Klass
        fields = (
            'instructor',
            # 'students',
            # 'teacher_assistants',
            'title',
            'course_number',
            'created',
            'modified',
            'group',
            'image',
            'enrolled_students',
            'active',
            'teams'
        )
