from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.db.models import Count, F
from django.http import Http404


from apps.profiles.models import StudentMembership, ChaUser, Instructor
from apps.homework.models import Submission
from apps.klasses.models import Klass


@api_view(['GET'])
@permission_classes(())
def chagrade_overall_metrics(request, version):
    data = {
        "users": ChaUser.objects.count(),
        "students": StudentMembership.objects.count(),
        "instructors": Instructor.objects.count(),
        "submissions": Submission.objects.count(),
        "klasses": Klass.objects.count(),
    }
    return Response(data, status=status.HTTP_200_OK)


class SubmissionMetricsView(APIView):
    def get(self, request, **kwargs):
        output_fields = {
            'count': Count('submitted_homeworks'),
            'name': F('user__username')
        }
        klass_pk = self.kwargs.get('klass_pk')
        if not klass_pk:
            raise Http404
        users = StudentMembership.objects.filter(klass__pk=klass_pk).values(**output_fields)
        return Response(users)

class StudentMetricsView(APIView):
    def get(self, request, **kwargs):
        output_fields = {
            'count': Count('pk'),
            'date': F('datefield')
        }
        users = StudentMembership.objects.dates('date_enrolled', 'day').values(**output_fields)
        return Response(users)

class InstructorMetricsView(APIView):
    def get(self, request, **kwargs):
        output_fields = {
            'count': Count('pk'),
            'date': F('datefield')
        }
        instructors = Instructor.objects.dates('date_promoted', 'day').values(**output_fields)
        return Response(instructors)

class KlassMetricsView(APIView):
    def get(self, request, **kwargs):
        output_fields = {
            'count': Count('pk'),
            'date': F('datefield')
        }
        klasses = Klass.objects.dates('created', 'day').values(**output_fields)
        return Response(klasses)
