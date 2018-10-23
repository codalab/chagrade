from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView, FormView, UpdateView
from django.views.generic.base import ContextMixin

from apps.klasses.forms import KlassForm
from apps.klasses.models import Klass

from apps.klasses.mixins import WizardMixin


class KlassCreationView(LoginRequiredMixin, FormView):
    template_name = 'klasses/klass_form.html'
    form_class = KlassForm
    success_url = reverse_lazy('profiles:instructor_overview')

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        new_obj.instructor = self.request.user.instructor
        new_obj.save()
        return super().form_valid(form)


class KlassEditView(LoginRequiredMixin, UpdateView):
    template_name = 'klasses/klass_form.html'
    form_class = KlassForm
    success_url = None
    model = Klass
    pk_url_kwarg = 'klass_pk'

    def get_success_url(self):
        if not self.success_url:
            return reverse_lazy('klasses:klass_details', kwargs={'klass_pk': self.object.pk})


class KlassOverView(LoginRequiredMixin, DetailView):
    template_name = 'klasses/wizard/overview.html'
    model = Klass
    pk_url_kwarg = 'klass_pk'


class KlassEnrollmentView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/enroll.html'


class KlassDefineHomeworkView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/define_homework.html'


class KlassGradeHomeworkView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/grade_homework.html'


class KlassActivateView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/activate_klass.html'
