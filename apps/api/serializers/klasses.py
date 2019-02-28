from rest_framework.serializers import ModelSerializer

from apps.api.serializers.groups import TeamSerializer
from apps.klasses.models import Klass
from apps.api.serializers.profiles import DetailedStudentSerializer


class KlassSerializer(ModelSerializer):
    enrolled_students = DetailedStudentSerializer(many=True, required=False)
    teams = TeamSerializer(many=True, required=False)

    class Meta:
        model = Klass
        fields = (
            'instructor',
            'title',
            'course_number',
            'created',
            'modified',
            'group',
            'image',
            'enrolled_students',
            'active',
            'teams',
        )
