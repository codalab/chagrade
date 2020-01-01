
import csv

from django.http import Http404, JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView, FormView, UpdateView

from apps.homework.models import Definition, Submission

from apps.klasses.forms import KlassForm
from apps.klasses.models import Klass
from apps.klasses.mixins import WizardMixin
from apps.profiles.models import StudentMembership

from apps.api.utils import get_unique_username


# Todo: Replace Http404's with correct response for forbidden (Besides not found?)


class CreationView(LoginRequiredMixin, FormView):
    template_name = 'klasses/klass_form.html'
    form_class = KlassForm
    success_url = reverse_lazy('profiles:instructor_overview')

    def form_valid(self, form):
        new_obj = form.save(commit=False)
        user = self.request.user
        new_obj.instructor = user.instructor
        new_obj.save()
        StudentMembership.objects.create(user=user, klass=new_obj, student_id=get_unique_username(user.username, user.email))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Create-Class'
        return context


class EditView(LoginRequiredMixin, UpdateView):
    template_name = 'klasses/klass_form.html'
    form_class = KlassForm
    success_url = None
    model = Klass
    pk_url_kwarg = 'klass_pk'

    def get_success_url(self):
        if not self.success_url:
            return reverse_lazy('klasses:klass_details', kwargs={'klass_pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Create-Class'
        return context


class OverView(LoginRequiredMixin, DetailView):
    template_name = 'klasses/wizard/overview.html'
    model = Klass
    pk_url_kwarg = 'klass_pk'

    def get_context_data(self, **kwargs):
        context = super(OverView, self).get_context_data(**kwargs)
        try:
            klass = kwargs.get('object')
        except ObjectDoesNotExist:
            raise Http404

        context['completely_graded'] = klass.homeworks_completely_graded()
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Instructor-Class-Detail'
        return context


class EnrollmentView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/enroll.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
        except ObjectDoesNotExist:
            raise Http404

        context['completely_graded'] = klass.homeworks_completely_graded()
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Wizard-Enroll-Students'
        return context


class DefineHomeworkView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/define_homework.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
        except ObjectDoesNotExist:
            raise Http404

        context['completely_graded'] = klass.homeworks_completely_graded()
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Wizard-Homework-List'
        return context


class GradeHomeworkView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/grade_homework.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
        except ObjectDoesNotExist:
            raise Http404

        context['completely_graded'] = klass.homeworks_completely_graded()
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Wizard-Grade-Homework'
        return context


class HomeworkAnswersView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/homework_answers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Homework-Answers'
        klass_pk = self.kwargs.get('klass_pk')
        klass = None
        try:
            klass = Klass.objects.get(pk=klass_pk)
            definition_pk = self.kwargs.get('definition_pk')
            definition = Definition.objects.get(pk=definition_pk)
            context['definition'] = definition
            question_quantity = definition.custom_questions.count()
            context['question_quantity_sensitive_width'] = question_quantity * 35
            context['question_quantity_range'] = range(question_quantity)

        except ObjectDoesNotExist:
            raise Http404("Could not find object!")

        try:
            instructor = klass.instructor
            context['instructor_student'] = klass.enrolled_students.get(user__pk=instructor.user.pk)
            context['instructor_submission'] = Submission.objects.filter(definition=definition, creator=context['instructor_student']).last()
            context['non_instructor_students'] = klass.enrolled_students.all().exclude(user__pk=instructor.user.pk).prefetch_related(Prefetch(
                'submitted_homeworks',
                queryset=Submission.objects.filter(definition=definition).order_by('created').prefetch_related('question_answers', 'question_answers__question', 'tracked_submissions'),
            ))

        except ObjectDoesNotExist:
            raise Http404("Instructor is not enrolled in class.")
        return context


# TODO: Make this into an API point/call
class ActivateView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'klasses/wizard/activate_klass.html'

    # Post view should just return some JSON with the new state, or an error message.
    def post(self, request, *args, **kwargs):
        # if not self.request.is_ajax():
        #     return HttpResponse(status=403)
        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
            if request.user == klass.instructor.user or request.user.is_superuser:
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
        except ObjectDoesNotExist:
            raise Http404

        context['klass'] = klass
        context['completely_graded'] = klass.homeworks_completely_graded()
        context['wiki_page_url'] = 'https://github.com/codalab/chagrade/wiki/Wizard-Activate-Class'
        return context


def get_klass_students_as_csv(request, klass_pk):
    if request.method == 'GET':
        # Create the HttpResponse object with the appropriate CSV header.
        klass = get_object_or_404(Klass, pk=klass_pk)
        if not (request.user.instructor == klass.instructor or request.user.is_superuser):
            raise Http404("Not allowed")

        response = HttpResponse(content_type='text/csv')
        temp_filename = 'class_{0}_students.csv'.format(klass_pk)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(temp_filename)

        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Display Name', 'Student ID', 'Email', 'Team'])
        for student in klass.enrolled_students.all():
            writer.writerow([student.user.first_name or '', student.user.last_name or '', student.user.username, student.student_id, student.user.email, student.team.name if student.team else ''])
        return response
    else:
        raise Http404("Only HTTP method GET is allowed.")


# def email_klass_students(request, klass_pk):
#     if request.method == 'POST':
#         # Create the HttpResponse object with the appropriate CSV header.
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
