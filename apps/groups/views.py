from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView, FormView

from apps.groups.forms import TeamForm
from apps.klasses.models import Klass


class TeamCreateView(LoginRequiredMixin, FormView):
    template_name = 'klasses/klass_form.html'
    form_class = TeamForm
    success_url = reverse_lazy('profiles:instructor_overview')

    def form_valid(self, form):
        try:
            new_obj = form.save(commit=False)
            new_obj.klass = Klass.objects.get(pk=self.kwargs.get('klass_pk'))
            # new_obj.instructor = self.request.user.instructor
            new_obj.save()
        except ObjectDoesNotExist:
            print("Could not find a klass to set to")
        return super().form_valid(form)
