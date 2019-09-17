from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from apps.klasses.mixins import WizardMixin

from apps.groups.models import Team


class TeamCreateView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'groups/forms/team_form.html'


class TeamEditView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'groups/forms/team_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_pk = self.kwargs.get('team_pk', None)
        team = get_object_or_404(Team, pk=team_pk)

        if team:
            context['team'] = team
        return context
