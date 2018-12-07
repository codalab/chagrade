from rest_framework.viewsets import ModelViewSet

from apps.api.serializers.groups import TeamSerializer
from apps.groups.models import Team


class TeamViewSet(ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = ()
