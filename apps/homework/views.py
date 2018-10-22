from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormMixin

from apps.homework.forms import HomeworkDefinitionForm
from apps.homework.models import HomeworkDefinition
from apps.klasses.mixins import WizardMixin
from apps.klasses.models import Klass


class DefineHomeworkFormView(LoginRequiredMixin, WizardMixin, FormMixin, TemplateView):
    template_name = 'homework/forms/define_homework.html'
    model = HomeworkDefinition
    form_class = HomeworkDefinitionForm
    success_url = reverse_lazy('klasses:klass_homework')

    def get_context_data(self, **kwargs):
        context = super(DefineHomeworkFormView, self).get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
            context['klass'] = klass
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        return context

    def form_valid(self, form):
        super(DefineHomeworkFormView, self).form_valid(form)
