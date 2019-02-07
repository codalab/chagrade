from rest_framework.viewsets import ModelViewSet

from apps.api.permissions import TeamPermissionCheck
from apps.api.serializers.groups import TeamSerializer
from apps.groups.models import Team


class TeamViewSet(ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = (TeamPermissionCheck,)

    def get_queryset(self):
        self.queryset = self.queryset.filter(klass__instructor__user=self.request.user)
        klass_pk = self.request.query_params.get('klass', None)
        if klass_pk is not None:
            self.queryset = self.queryset.filter(klass__pk=klass_pk)
        return self.queryset
