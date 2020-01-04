import csv

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.db.models import Subquery, OuterRef, F, Count, When, Case, Value, BooleanField
from django.views.generic import TemplateView

from rest_framework.exceptions import PermissionDenied

from apps.homework.models import Definition, Grade, Submission
from apps.klasses.mixins import WizardMixin
from apps.klasses.models import Klass


class DefinitionFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/define_homework.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Create-and-Edit-Homework'
        return context


class DefinitionEditFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/define_homework.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['definition'] = Definition.objects.get(pk=self.kwargs.get('definition_pk'))
            context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Create-and-Edit-Homework'
            return context
        except ObjectDoesNotExist:
            raise Http404("Failed to retrieve definition")


class GradeFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/grade_homework.html'

    def get_context_data(self, **kwargs):
        context = super(GradeFormView, self).get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Grade-Submission'
        try:
            context['submission'] = Submission.objects.get(pk=kwargs.get('submission_pk'))
            context['definition'] = context['submission'].definition
        except ObjectDoesNotExist:
            raise Http404("Could not find submission!")
        return context


class GradeEditFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/grade_homework.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Grade-Submission'
        try:
            context['submission'] = Submission.objects.get(pk=self.kwargs.get('submission_pk'))
            context['definition'] = context['submission'].definition
            context['grade'] = Grade.objects.get(pk=self.kwargs.get('grade_pk'))
        except ObjectDoesNotExist:
            raise Http404("Could not find object!")
        return context


class HomeworkOverView(LoginRequiredMixin, TemplateView):
    template_name = 'homework/overview.html'
    model = Submission

    def get_context_data(self, **kwargs):
        context = super(HomeworkOverView, self).get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Homework-Overview'
        klass_pk = self.kwargs.get('klass_pk')
        try:
            klass = Klass.objects.get(pk=klass_pk)
            context['klass'] = klass
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')

        student = klass.enrolled_students.get(user=self.request.user)
        context['definitions'] = klass.homework_definitions.all().annotate(
            number_of_submissions_made=Subquery(Submission.objects.filter(creator=student, definition=OuterRef('pk')).values('definition__pk').annotate(total_subs=Count('pk')).values('total_subs'))
        ).annotate(
            max_submission_limit_met=Case(
                When(number_of_submissions_made__gte=F('max_submissions_per_student'), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        return context


class SubmissionDetailView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'homework/submission_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SubmissionDetailView, self).get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Submission-Detail'
        submission_pk = self.kwargs.get('submission_pk')
        try:
            submission = Submission.objects.get(pk=submission_pk)
            context['submission'] = submission
            context['definition'] = submission.definition
            context['klass'] = submission.klass
            context['logs_possible'] = [
                'inputfile',
                'stdout_file',
                'stderr_file',
                'scores_file',
                'prediction_runfile',
                'prediction_output_file',
                'exception_details',
                'prediction_stdout_file',
                'prediction_stderr_file',
                'ingestion_program_stdout_file',
                'ingestion_program_stderr_file',
            ]
            context['files_possible'] = [
                'output_file',
                'private_output_file',
                'detailed_results_file',
                's3_file',
                'file',
            ]
        except ObjectDoesNotExist:
            raise Http404('Definition object not found')
        return context

    def test_func(self):
        submission_pk = self.kwargs.get('submission_pk')
        try:
            submission = Submission.objects.get(pk=submission_pk)
        except ObjectDoesNotExist:
            raise Http404('Definition object not found')
        if self.request.user.is_superuser:
            return True
        if self.request.user.instructor:
            if self.request.user.instructor == submission.definition.klass.instructor:
                return True
        try:
            if self.request.user.klass_memberships.get(klass__pk=submission.definition.klass.pk):
                return True
        except ObjectDoesNotExist:
            return False
        return False


class SubmissionListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'homework/submission_list.html'

    def get_context_data(self, **kwargs):
        context = super(SubmissionListView, self).get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Submission-List'
        definition_pk = self.kwargs.get('definition_pk')
        submissions = None
        try:
            definition = Definition.objects.get(pk=definition_pk)
            context['definition'] = definition
            context['klass'] = definition.klass
        except ObjectDoesNotExist:
            raise Http404('Definition object not found')

        # if user is instructor of the class
        if self.request.user.instructor and self.request.user.instructor == definition.klass.instructor:
            try:
                submissions = Submission.objects.filter(definition=definition)
                context['instructor_view'] = True
            except ObjectDoesNotExist:
                raise Http404('Submission object not found')

        # if user is member of the class
        else:
            try:
                klass_membership = self.request.user.klass_memberships.get(klass__pk=definition.klass.pk)
            except ObjectDoesNotExist:
                raise HttpResponseForbidden('Student Membership object not found')
            try:
                if definition.team_based:
                    team = klass_membership.team
                    submissions = Submission.objects.filter(definition=definition, team=team)
                    context['team'] = team
                else:
                    submissions = Submission.objects.filter(definition=definition, creator=klass_membership)
            except ObjectDoesNotExist:
                raise HttpResponseForbidden('Submission object not found')
        context['submissions'] = submissions
        context['user'] = self.request.user
        return context

    def test_func(self):
        definition_pk = self.kwargs.get('definition_pk')
        try:
            definition = Definition.objects.get(pk=definition_pk)
        except ObjectDoesNotExist:
            raise Http404('Definition object not found')
        if self.request.user.is_superuser:
            return True
        if self.request.user.instructor:
            if self.request.user.instructor == definition.klass.instructor:
                return True
        try:
            if self.request.user.klass_memberships.get(klass__pk=definition.klass.pk):
                return True
        except ObjectDoesNotExist:
            return False
        return False


class SubmissionFormView(LoginRequiredMixin, TemplateView):
    template_name = 'homework/forms/submit.html'

    def get_context_data(self, use_github=False, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Submit-Homework'
        try:
            if use_github and self.request.user.github_info:
                context['github'] = True

            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
            context['klass'] = klass
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        try:
            definition = Definition.objects.get(pk=kwargs.get('definition_pk'))
            context['definition'] = definition
        except ObjectDoesNotExist:
            raise Http404('Definition object not found')
        try:
            context['student'] = klass.enrolled_students.get(user=self.request.user)
        except ObjectDoesNotExist:
            raise HttpResponseForbidden('User not part of klass.')

        student = klass.enrolled_students.get(user=self.request.user)
        submission_count = Submission.objects.filter(definition=definition, creator=student).count()
        if submission_count >= definition.max_submissions_per_student:
            raise PermissionDenied("You've reached the submission limit for this homework.")
        return context


class SubmissionEditFormView(LoginRequiredMixin, TemplateView):
    template_name = 'homework/forms/submit.html'

    def get_context_data(self, use_github=False, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Submit-Homework'
        try:
            klass = Klass.objects.get(pk=self.kwargs.get('klass_pk'))
            submission = Submission.objects.get(pk=self.kwargs.get('submission_pk'))
            student = klass.enrolled_students.get(user=self.request.user)

            definition = Definition.objects.get(pk=kwargs.get('definition_pk'))
            context['definition'] = definition

            if definition.team_based:
                if not submission.creator == student or not student in submission.team.members.all():
                    raise HttpResponseForbidden("You do not have permission to view this")
            else:
                if not submission.creator == student:
                    raise HttpResponseForbidden("You do not have permission to view this")

            if use_github and self.request.user.github_info:
                context['github'] = True

            context['submission'] = submission
            context['klass'] = klass
            definition = Definition.objects.get(pk=kwargs.get('definition_pk'))
            context['definition'] = definition
            context['student'] = student
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        return context


def get_klass_grades_as_csv(request, klass_pk):
    if request.method == 'GET':
        # Create the HttpResponse object with the appropriate CSV header.
        try:
            klass = Klass.objects.get(pk=klass_pk)
            response = HttpResponse(content_type='text/csv')
            temp_filename = 'class_{0}_grades.csv'.format(klass_pk)
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(temp_filename)

            writer = csv.writer(response)
            first_row = ['Student-ID', 'Student-Email']
            for definition in klass.homework_definitions.all():
                first_row.append('{} - Grade:'.format(definition.name))
            writer.writerow(first_row)
            for student in klass.enrolled_students.all():
                temp_student_row = [student.student_id, student.user.email]
                for definition in klass.homework_definitions.all():
                    if definition.team_based:
                        last_submission = definition.submissions.filter(team=student.team).last()
                    else:
                        last_submission = definition.submissions.filter(creator=student).last()
                    if last_submission:
                        published_grades = last_submission.grades.filter(published=True)
                        last_grade = published_grades.last() if published_grades.count() > 0 else None
                        # temp_student_row.append(last_grade.overall_grade)
                        if last_grade:
                            temp_student_row.append(last_grade.text_grade)
                        else:
                            temp_student_row.append('N/A')
                    else:
                        temp_student_row.append(0)
                writer.writerow(temp_student_row)
            return response
        except ObjectDoesNotExist:
            raise Http404("Klass not found!")
    else:
        raise Http404("Only HTTP method GET is allowed.")
