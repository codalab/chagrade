import pprint

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import F, Subquery, OuterRef

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_csv import renderers

from apps.api.permissions import KlassPermissionCheck

from apps.api.serializers.klasses import KlassSerializer

from apps.api.permissions import InstructorOrSuperuserPermission

from apps.klasses.models import Klass
from apps.profiles.models import StudentMembership
from apps.homework.models import Submission, QuestionAnswer, Definition

User = get_user_model()


def format_list_to_string(input_list):
    outstring = ''
    delimiter = ',\n'

    for i, word in enumerate(input_list):
        if i < len(input_list) - 1:
            outstring += str(word) + delimiter
        else:
            outstring += str(word)
    return outstring


class EnrollStudentsRenderer(renderers.CSVRenderer):
    labels = {
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'username': 'Username',
        'student_id': 'Student ID',
        'email': 'Student Email',
        'team_name': 'Team Name',
        'team_leader': 'Team Leader',
    }
    header = list(labels.keys())


class HomeworkAnswersRenderer(renderers.CSVRenderer):
    labels = {
        'name': 'Student Name',
    }
    header = list(labels.keys())


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


class HomeworkAnswersCSVView(APIView):
    """Get homework scores and question answers for entire klass."""
    renderer_classes = (HomeworkAnswersRenderer,)
    permission_classes = (InstructorOrSuperuserPermission,)

    def get(self, request, **kwargs):
        klass_pk = kwargs.get('klass_pk')
        definition_pk = kwargs.get('definition_pk')

        definition = get_object_or_404(Definition, pk=definition_pk)
        values_fields = {
            'name': F('student_id'),
        }

        students = StudentMembership.objects.filter(klass=klass_pk)

        if not definition.questions_only:
            values_fields.update({'score': F('score')})

            if definition.team_based:
                print('team based')
                students = students.annotate(score=Subquery(
                    definition.submissions.filter(team=OuterRef('team__pk')).order_by('-created').values(
                        'tracked_submissions__stored_score')[:1]))
                self.renderer_classes[0].labels['score'] = 'Team Score'
            else:
                print('not team based')
                students = students.annotate(score=Subquery(
                    definition.submissions.filter(creator=OuterRef('pk')).order_by('-created').values(
                        'tracked_submissions__stored_score')[:1]))
                self.renderer_classes[0].labels['score'] = 'Student Score'

        # for every question with index N, call the field name on the csv 'qN' with human-readable
        # label q.question.

        questions = definition.custom_questions.all()

        for i, question in enumerate(questions):
            self.renderer_classes[0].labels['q' + str(i)] = question.question

        self.renderer_classes[0].header = list(self.renderer_classes[0].labels.keys())

        # Annotate most recent submissions's pk to students

        if definition.team_based:
            students = students.annotate(last_submission=Subquery(
                definition.submissions.filter(team=OuterRef('team__pk')).order_by('-created').values(
                    'pk')[:1]))
        else:
            students = students.annotate(last_submission=Subquery(
                definition.submissions.filter(creator=OuterRef('pk')).order_by('-created').values(
                    'pk')[:1]))

        students_list = list(students.values(**values_fields))

        for i, student in enumerate(students):
            try:
                last_sub = Submission.objects.get(pk=student.last_submission)
            except Submission.DoesNotExist:
                continue
            answers = last_sub.question_answers.all()
            if len(list(answers)) == len(list(questions)):
                for j, question in enumerate(questions):
                    students_list[i]['q' + str(j)] = format_list_to_string(answers[j].answer)

        return Response(students_list)


class EnrollStudentsSampleCSVView(APIView):
    """Generate a sample csv in the proper upload format for student enrollment."""
    renderer_classes = (EnrollStudentsRenderer,)

    def get(self, request, **kwargs):
        sample_output = [
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'username': 'johnnyboy25',
                'student_id': '1421141',
                'email': 'john@email.com',
                'team_name': 'Smashing Pumpkins',
                'team_leader': 'True',
            }, {
                'first_name': 'Samantha',
                'last_name': 'Higgs',
                'username': 'samsam',
                'student_id': '1421028',
                'email': 'sam@email.com',
                'team_name': 'Gradient Descenders',
                'team_leader': 'True',
            }, {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'username': 'itsjanedoe',
                'student_id': '1421241',
                'email': 'jane@email.com',
                'team_name': 'Smashing Pumpkins',
                'team_leader': '',
            }
        ]

        return Response(sample_output)
