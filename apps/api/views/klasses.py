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
