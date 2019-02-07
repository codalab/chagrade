import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView, FormView

# from apps.groups.forms import TeamForm
from apps.groups.models import Team
from apps.klasses.mixins import WizardMixin
from apps.klasses.models import Klass
from apps.profiles.models import StudentMembership


class TeamCreateView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'groups/forms/team_form.html'


class TeamEditView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'groups/forms/team_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.request.kwargs.get('team', None)
        if team:
            context['team'] = team
        return context