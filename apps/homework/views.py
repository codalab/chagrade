from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, JsonResponse
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
