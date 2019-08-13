from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.db.models import Count, F, OuterRef, Max, Avg, Subquery
from django.http import Http404


from apps.profiles.models import StudentMembership, ChaUser, Instructor
from apps.homework.models import Submission, Definition, SubmissionTracker
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

class StudentScoresView(APIView):
    def get(self, request, **kwargs):
        output_fields = {
            'score': Count('pk'),
            'date': F('datefield')
        }
        student = StudentMembership.objects.get(pk=kwargs.get('student_id'))

       # TODO: Add Permissions Class (403 rather than 404)
        # Is instructor of student's klass
        if not request.user.instructor == student.klass.instructor:
            raise Http404

        Submission.objects.filter(creator=student).dates('created', 'day').values(score=Avg('normalized_score'), date=F('datefield'))

        return Response()

class KlassScoresView(APIView):
    def get(self, request, **kwargs):
        output_fields = {
            'score': Count('pk'),
            'date': F('datefield')
        }

        klass_pk = kwargs.get('klass_pk')

        # TODO: Add Permissions Class (403 rather than 404)
        # Is instructor of student's klass
#        if not request.user.instructor == student.klass.instructor:
#            raise Http404

#        score_query = Submission.objects.filter(definition__pk=OuterRef(OuterRef('pk')), creator__pk=OuterRef('pk')).annotate(
#            score=Max('tracked_submissions__stored_score')).values('score')
        #'tracked_submissions__stored_score'
        tracker_score_query = SubmissionTracker.objects.filter(submission=OuterRef('pk')).values('stored_score')

        sub_score_query = Submission.objects.filter(definition=5, creator=OuterRef('pk')).annotate(score=Max(Subquery(tracker_score_query))).values('score')

        student_query = StudentMembership.objects.filter(klass=klass_pk).annotate(best_score=Max(Subquery(sub_score_query))).values('best_score')

        definition_query = Definition.objects.filter(klass=klass_pk).annotate(avg_score=Avg(Subquery(student_query)))

#        definition_query = Definition.objects.filter(klass__pk=klass_pk).annotate(avg_score=Subquery(
#            Submission.objects.filter(definition=OuterRef('pk')).values('tracked_submissions')
#        ))

        print(definition_query)
        return Response()
