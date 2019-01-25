import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
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
        return context


class EnrollmentView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/enroll.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DefineHomeworkView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/define_homework.html'


class GradeHomeworkView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/grade_homework.html'


# TODO: Make this into an API point/call
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


def get_klass_students_as_csv(request, klass_pk):
    if request.method == 'GET':
        # Create the HttpResponse object with the appropriate CSV header.

        print(request)

        try:
            klass = Klass.objects.get(pk=klass_pk)
            response = HttpResponse(content_type='text/csv')
            temp_filename = 'class_{0}_students.csv'.format(klass_pk)
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(temp_filename)

            writer = csv.writer(response)
            writer.writerow(['First Name', 'Last Name', 'Display Name', 'Student ID', 'Email', 'Team'])
            for student in klass.enrolled_students.all():
                writer.writerow([student.user.first_name or '', student.user.last_name or '', student.user.username, student.student_id, student.user.email, student.team.name or ''])
            return response
        except ObjectDoesNotExist:
            raise Http404("Klass not found!")
    else:
        raise Http404("Only HTTP method GET is allowed.")


# def email_klass_students(request, klass_pk):
#     if request.method == 'POST':
#         # Create the HttpResponse object with the appropriate CSV header.
#
#         print(request)
#         # print(request.data)
#         # print(request.validated_data)
#         print("@@@@@@@@@@@@@@@")
#         print(request.POST)
#         print(request.body)
#         data = request.POST
#         print(data)
#         print(request.POST.get('message'))
#         print("@@@@@@@@@@@@@@@")
#
#         try:
#             subject = request.POST.get('subject')
#             message = request.POST.get('message')
#             recepients = []
#             klass = Klass.objects.get(pk=klass_pk)
#             for student in klass.enrolled_students.all():
#                 recepients.append(student.user.email)
#             send_mail(
#                 subject,
#                 message,
#                 'from@chagrade.com',
#                 recepients,
#                 fail_silently=False,
#             )
#             data = {
#                 'status': 200,
#                 'message': 'Succesfully sent messages!'
#             }
#             return JsonResponse(data, status=200)
#         except ObjectDoesNotExist:
#             # raise Http404("Klass not found!")
#             data = {
#                 'status': 404,
#                 'errors': {'klass': "Klass object not found!"}
#             }
#             return JsonResponse(data, status=404)
#     else:
#         # raise Http404("Only HTTP method POST is allowed.")
#         data = {
#             'status': 405,
#             'errors': {'method': "Method not allowed!"}
#         }
#         return JsonResponse(data, status=404)

# TODO: Make this into an API point/view(?)
class EmailKlassStudentsView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/activate_klass.html'

    # Post view should just return some JSON with the new state, or an error message.
    def post(self, request, *args, **kwargs):
        # Create the HttpResponse object with the appropriate CSV header.

        print(request)
        # print(request.data)
        # print(request.validated_data)
        print("@@@@@@@@@@@@@@@")
        print(request.POST)
        # print(request.body)
        data = request.POST
        print(data)
        print(request.POST.get('message'))
        print("@@@@@@@@@@@@@@@")

        try:
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            recepients = []
            klass = Klass.objects.get(pk=self.kwargs.get('klass_pk'))
            for student in klass.enrolled_students.all():
                recepients.append(student.user.email)
            send_mail(
                subject,
                message,
                'from@chagrade.com',
                recepients,
                fail_silently=False,
            )
            data = {
                'status': 200,
                'message': 'Succesfully sent messages!'
            }
            return JsonResponse(data, status=200)
        except ObjectDoesNotExist:
            # raise Http404("Klass not found!")
            data = {
                'status': 404,
                'errors': {'klass': "Klass object not found!"}
            }
            return JsonResponse(data, status=404)
