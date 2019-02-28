from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from apps.klasses.mixins import WizardMixin
# Create your views here.


class TeamCreateView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'groups/forms/team_form.html'


class TeamEditView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'groups/forms/team_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.kwargs.get('team_pk', None)
        if team:
            context['team'] = team
        return context
