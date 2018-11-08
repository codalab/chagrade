from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView, FormView, UpdateView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin
from rest_framework import status
from rest_framework.response import Response

from apps.klasses.forms import KlassForm
from apps.klasses.models import Klass

from apps.klasses.mixins import WizardMixin


class CreationView(LoginRequiredMixin, FormView):
    template_name = 'klasses/klass_form.html'
    form_class = KlassForm
    success_url = reverse_lazy('profiles:instructor_overview')

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        new_obj.instructor = self.request.user.instructor
        new_obj.save()
        return super().form_valid(form)


class EditView(LoginRequiredMixin, UpdateView):
    template_name = 'klasses/klass_form.html'
    form_class = KlassForm
    success_url = None
    model = Klass
    pk_url_kwarg = 'klass_pk'

    def get_success_url(self):
        if not self.success_url:
            return reverse_lazy('klasses:klass_details', kwargs={'klass_pk': self.object.pk})


class OverView(LoginRequiredMixin, DetailView):
    template_name = 'klasses/wizard/overview.html'
    model = Klass
    pk_url_kwarg = 'klass_pk'

    def get_context_data(self, **kwargs):
        context = super(OverView, self).get_context_data(**kwargs)
        print(kwargs)
        return context


class EnrollmentView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/enroll.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("!!!!!!!!!!!!!!!!")
        print(kwargs)
        return context


class DefineHomeworkView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/define_homework.html'


class GradeHomeworkView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/grade_homework.html'


class ActivateView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/activate_klass.html'

    # Post view should just return some JSON with the new state, or an error message.
    def post(self, request, *args, **kwargs):
        # if not self.request.is_ajax():
        #     return HttpResponse(status=403)
        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
            if request.user == klass.instructor.user:
                klass.active = not klass.active
                klass.save()
                data = {
                    'status': 200,
                    'new_state': klass.active,
                }
                return JsonResponse(data, status=200)
            else:
                data = {
                    'status': 403,
                    'errors': {'user': "You're not allowed to edit this klass"}
                }
                return JsonResponse(data, status=403)
        except ObjectDoesNotExist:
            data = {
                'status': 404,
                'errors': {'klass': "Klass object not found!"}
            }
            return JsonResponse(data, status=404)
