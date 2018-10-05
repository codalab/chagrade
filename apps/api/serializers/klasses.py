from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

from apps.klasses.models import Klass


class KlassSerializer(ModelSerializer):
    from apps.api.serializers.profiles import InstructorSerializer

    instructor = InstructorSerializer()

    class Meta:
        model = Klass
        fields = (
            'instructor',
            'students',
            'teacher_assistants',
            'title',
            'course_number',
            'created',
            'modified',
            'group',
            'image',
        )
