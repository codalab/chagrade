from drf_writable_nested import WritableNestedModelSerializer
from rest_framework.serializers import ModelSerializer

from apps.groups.models import Team

from apps.api.serializers.profiles import StudentSerializer


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
        read_only_fields = ['submissions']


class BasicTeamSerializer(ModelSerializer):

    class Meta:
        model = Team
        fields = [
            'name',
            'description',
        ]
