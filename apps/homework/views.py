import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormMixin, FormView, CreateView, UpdateView

from apps.homework.forms import DefinitionForm, GradeForm, SubmissionForm, DefinitionEditForm
from apps.homework.models import Definition, Grade, Submission, Question, Criteria
from apps.klasses.mixins import WizardMixin
from apps.klasses.models import Klass
from apps.profiles.models import Instructor


class DefinitionFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/define_homework.html'


class DefinitionEditFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/define_homework.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['definition'] = Definition.objects.get(pk=self.kwargs.get('definition_pk'))
            return context
        except ObjectDoesNotExist:
            raise Http404("Failed to retrieve definition")


class GradeFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/grade_homework.html'

    def get_context_data(self, **kwargs):
        context = super(GradeFormView, self).get_context_data(**kwargs)
        try:
            context['submission'] = Submission.objects.get(pk=kwargs.get('submission_pk'))
            context['definition'] = context['submission'].definition
        except:
            raise Http404("Could not find submission!")
        return context


class GradeEditFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/grade_homework.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['submission'] = Submission.objects.get(pk=self.kwargs.get('submission_pk'))
            context['definition'] = context['submission'].definition
            context['grade'] = Grade.objects.get(pk=self.kwargs.get('grade_pk'))
        except:
            raise Http404("Could not find submission!")
        return context


class SubmissionOverView(LoginRequiredMixin, TemplateView):
    template_name = 'homework/overview.html'
    model = Submission

    def get_context_data(self, **kwargs):
        context = super(SubmissionOverView, self).get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=self.kwargs.get('klass_pk'))
            context['klass'] = klass
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        return context


class SubmissionFormView(LoginRequiredMixin, TemplateView):
    template_name = 'homework/forms/submit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
            context['klass'] = klass
            definition = Definition.objects.get(pk=kwargs.get('definition_pk'))
            context['definition'] = definition
            context['student'] = klass.enrolled_students.get(user=self.request.user)
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        return context


class SubmissionEditFormView(LoginRequiredMixin, TemplateView):
    template_name = 'homework/forms/submit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=self.kwargs.get('klass_pk'))
            submission = Submission.objects.get(pk=self.kwargs.get('submission_pk'))
            context['submission'] = submission
            context['klass'] = klass
            definition = Definition.objects.get(pk=kwargs.get('definition_pk'))
            context['definition'] = definition
            context['student'] = klass.enrolled_students.get(user=self.request.user)
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        return context


def get_klass_grades_as_csv(request, klass_pk):
    if request.method == 'GET':
        # Create the HttpResponse object with the appropriate CSV header.

        print(request)

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
                    last_submission = definition.submissions.filter(creator=student).last()
                    if last_submission:
                        published_grades = last_submission.grades.filter(published=True)
                        last_grade = published_grades.last() if published_grades.count() > 0 else None
                        temp_student_row.append(last_grade.overall_grade)
                    else:
                        temp_student_row.append(0)
                writer.writerow(temp_student_row)
            return response
        except ObjectDoesNotExist:
            raise Http404("Klass not found!")
    else:
        raise Http404("Only HTTP method GET is allowed.")
