from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.serializers import ModelSerializer

from apps.groups.models import Team

from apps.api.serializers.profiles import StudentSerializer, DetailedStudentSerializer


# class TeamSerializer(ModelSerializer):
class TeamSerializer(WritableNestedModelSerializer):

    members = StudentSerializer(many=True)

    class Meta:
        model = Team
        fields = [
            'klass',
            'id',
            'name',
            'description',
            'members',
        ]


class BasicTeamSerializer(ModelSerializer):

    class Meta:
        model = Team
        fields = [
            'name',
            'description',
        ]
