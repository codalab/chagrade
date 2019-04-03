from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet

from apps.api.permissions import KlassPermissionCheck

from apps.api.serializers.klasses import KlassSerializer

from apps.klasses.models import Klass

User = get_user_model()


class KlassViewSet(ModelViewSet):
    """Updating and inserting competitions are done by Producers."""
    queryset = Klass.objects.all()
    serializer_class = KlassSerializer
    permission_classes = (KlassPermissionCheck,)

    def get_queryset(self):
        # self.queryset = self.queryset.filter(instructor__user=self.request.user)
        instructor_pk = self.request.query_params.get('instructor', None)
        if instructor_pk is not None:
            self.queryset = self.queryset.filter(instructor__pk=instructor_pk)
        return self.queryset
