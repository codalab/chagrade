from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormMixin

from apps.homework.forms import DefinitionForm, GradeForm, SubmissionForm
from apps.homework.models import Definition, Grade, Submission
from apps.klasses.mixins import WizardMixin
from apps.klasses.models import Klass


class DefinitionFormView(LoginRequiredMixin, WizardMixin, FormMixin, TemplateView):
    template_name = 'homework/forms/define_homework.html'
    model = Definition
    form_class = DefinitionForm
    # success_url = reverse_lazy('klasses:klass_homework')

    def form_valid(self, form):
        super(DefinitionFormView, self).form_valid(form)


class GradeFormView(LoginRequiredMixin, WizardMixin, FormMixin, TemplateView):
    template_name = 'homework/forms/grade_homework.html'
    model = Grade
    form_class = GradeForm
    # success_url = reverse_lazy('klasses:klass_homework')

    def form_valid(self, form):
        super(GradeFormView, self).form_valid(form)


class SubmissionFormView(LoginRequiredMixin, FormMixin, TemplateView):
    template_name = 'homework/forms/submit_homework.html'
    model = Submission
    form_class = SubmissionForm
    success_url = reverse_lazy('profiles:student_overview')

    def get_context_data(self, **kwargs):
        context = super(SubmissionFormView, self).get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
            context['klass'] = klass
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        return context

    def form_valid(self, form):
        super(SubmissionFormView, self).form_valid(form)
