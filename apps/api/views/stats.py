from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.homework.models import Submission
from apps.klasses.models import Klass
from apps.profiles.models import StudentMembership, ChaUser


@api_view(['GET'])
@permission_classes(())
def chagrade_general_stats(request, version):
    data = {
        "students": StudentMembership.objects.count(),
        "users": ChaUser.objects.count(),
        "submissions": Submission.objects.count(),
        "klasses": Klass.objects.count(),
    }

    return Response(data, status=status.HTTP_200_OK)
