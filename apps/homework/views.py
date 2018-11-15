from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormMixin, FormView, CreateView, UpdateView

from apps.homework.forms import DefinitionForm, GradeForm, SubmissionForm, DefinitionEditForm
from apps.homework.models import Definition, Grade, Submission, Question, Criteria
from apps.klasses.mixins import WizardMixin
from apps.klasses.models import Klass
from apps.profiles.models import Instructor


# class DefinitionFormView(LoginRequiredMixin, WizardMixin, FormMixin, TemplateView):
#     template_name = 'homework/forms/define_homework.html'
#     model = Definition
#     form_class = DefinitionForm
#     success_url = None
#
#     # def get_success_url(self):
#     #     klass_pk =
#     #     return reverse_lazy('klasses:klass_homework')
#
#     # def clean_question_data(self, question_data):
#     #     for key, value in question_data:
#     #         # If we're not a boolean and we're null, an empty string, an empty list, etc
#     #         if type(value) != bool and not value or len(value) == 0:
#     #             print("A question value was null or not valid")
#     #             return reverse_lazy('homework:define_homework', kwargs={'klass_pk': self.kwargs.get('klass_pk')})
#
#     def clean_criteria(self, index, post_data):
#         refs = [
#             'criteria_{}_description'.format(index),
#             'criteria_{}_low_range'.format(index),
#             'criteria_{}_high_range'.format(index),
#         ]
#         # Check we have data for all inputs
#         for data_ref in refs:
#             if not post_data.get(data_ref):
#                 return False
#         # Check that our lowest range isn't greater than our highest range
#         if post_data.get(refs[1]) > post_data.get(refs[2]):
#             return False
#         return True
#
#     def clean_questions(self, post_data):
#         # if post_data.get('question_0_text'):
#         have_question = True
#         count = 0
#         while have_question:
#             if post_data.get('question_{}_text'.format(count)):
#                 count += 1
#             else:
#                 have_question = False
#         print("We validated all questions")
#         return count
#
#     def clean_criterias(self, post_data):
#         # if post_data.get('question_0_text'):
#         have_criteria = True
#         count = 0
#         while have_criteria:
#             if post_data.get('criteria_{}_description'.format(count)):
#                 result = self.clean_criteria(count, post_data)
#                 if not result:
#                     raise Http404("Could not validate data")
#                 count += 1
#             else:
#                 have_criteria = False
#         print("We validated all criterias")
#         return count
#
#     def post(self, request, *args, **kwargs):
#         """
#         Handle POST requests: instantiate a form instance with the passed
#         POST variables and then check if it's valid.
#         """
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)
#
#     def form_valid(self, form):
#         print(self.request.POST)
#         obj = form.save(commit=False)
#         try:
#             klass = Klass.objects.get(pk=self.kwargs.get('klass_pk'))
#             obj.klass = klass
#         except ObjectDoesNotExist:
#             raise Http404("Klass object not found for definition")
#         try:
#             creator = Instructor.objects.get(user=self.request.user)
#             obj.creator = creator
#         except ObjectDoesNotExist:
#             raise Http404("Could not find instructor for current user")
#
#         obj.save()
#
#         validated_question_count = self.clean_questions(self.request.POST)
#         for index in range(validated_question_count):
#             has_answer = True if self.request.POST.get('question_{}_has_answer'.format(index)) == 'on' else False
#             new_question = Question.objects.create(
#                 definition=obj,
#                 question=self.request.POST.get('question_{}_text'.format(index)),
#                 answer=self.request.POST.get('question_{}_answer'.format(index), ''),
#                 has_specific_answer=has_answer,
#             )
#
#         validated_criteria_count = self.clean_criterias(self.request.POST)
#         for index in range(validated_criteria_count):
#             # has_answer = True if self.request.POST.get('question_{}_has_answer'.format(index)) == 'on' else False
#             new_criteria = Criteria.objects.create(
#                 definition=obj,
#                 description=self.request.POST.get('criteria_{}_description'.format(index)),
#                 lower_range=self.request.POST.get('criteria_{}_low_range'.format(index)),
#                 upper_range=self.request.POST.get('criteria_{}_high_range'.format(index))
#             )
#
#         # super(DefinitionFormView, self).form_valid(form)
#         return HttpResponseRedirect(reverse_lazy('klasses:klass_homework', kwargs={'klass_pk': self.kwargs.get('klass_pk')}))
#
#
# class DefinitionEditFormView(LoginRequiredMixin, WizardMixin, UpdateView):
#     # template_name = 'homework/forms/define_homework.html'
#     # model = Definition
#     # form_class = DefinitionForm
#     # success_url = None
#     #
#     # def post(self, request, *args, **kwargs):
#     #     """
#     #     Handle POST requests: instantiate a form instance with the passed
#     #     POST variables and then check if it's valid.
#     #     """
#     #     form = self.get_form()
#     #     if form.is_valid():
#     #         return self.form_valid(form)
#     #     else:
#     #         return self.form_invalid(form)
#     #
#     # def form_valid(self, form):
#     #     print(self.request.POST)
#     #     obj = form.save(commit=False)
#     #     try:
#     #         klass = Klass.objects.get(pk=self.kwargs.get('klass_pk'))
#     #         obj.klass = klass
#     #     except ObjectDoesNotExist:
#     #         raise Http404("Klass object not found for definition")
#     #     try:
#     #         creator = Instructor.objects.get(user=self.request.user)
#     #         obj.creator = creator
#     #     except ObjectDoesNotExist:
#     #         raise Http404("Could not find instructor for current user")
#     #
#     #     obj.save()
#     #
#     #     return HttpResponseRedirect(reverse_lazy('klasses:klass_homework', kwargs={'klass_pk': self.kwargs.get('klass_pk')}))
#     template_name = 'homework/forms/define_homework.html'
#     form_class = DefinitionForm
#     success_url = None
#     model = Definition
#     pk_url_kwarg = 'definition_pk'
#
#     def get_context_data(self, **kwargs):
#         context = super(DefinitionEditFormView, self).get_context_data(**kwargs)
#         try:
#             context['definition'] = Definition.objects.get(pk=self.kwargs.get('definition_pk'))
#         except ObjectDoesNotExist:
#             raise Http404("Could not find definition!")
#         context['is_edit_page'] = True
#         return context
#
#     def get_success_url(self):
#         if not self.success_url:
#             return HttpResponseRedirect(
#                 reverse_lazy('klasses:klass_homework', kwargs={'klass_pk': self.kwargs.get('klass_pk')}))
#             # return reverse_lazy('klasses:klass_details', kwargs={'klass_pk': self.object.pk})

class DefinitionFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/define_homework.html'


class DefinitionEditFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/define_homework.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['definition'] = Definition.objects.get(pk=self.kwargs.get('definition_pk'))
            return context
        except ObjectDoesNotExist:
            raise Http404("Failed to retrieve definition")


class GradeFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/grade_homework.html'

    def get_context_data(self, **kwargs):
        context = super(GradeFormView, self).get_context_data(**kwargs)
        try:
            context['submission'] = Submission.objects.get(pk=kwargs.get('submission_pk'))
            context['definition'] = context['submission'].definition
        except:
            raise Http404("Could not find submission!")
        return context


class GradeEditFormView(LoginRequiredMixin, WizardMixin, TemplateView):
    template_name = 'homework/forms/grade_homework.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['submission'] = Submission.objects.get(pk=self.kwargs.get('submission_pk'))
            context['definition'] = context['submission'].definition
            context['grade'] = Grade.objects.get(pk=self.kwargs.get('grade_pk'))
        except:
            raise Http404("Could not find submission!")
        return context


class SubmissionOverView(LoginRequiredMixin, TemplateView):
    template_name = 'homework/overview.html'
    model = Submission
    # form_class = SubmissionForm
    # success_url = reverse_lazy('homework:homework_overview')

    def get_context_data(self, **kwargs):
        context = super(SubmissionOverView, self).get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=self.kwargs.get('klass_pk'))
            context['klass'] = klass
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        return context

    # def form_valid(self, form):
    #     super().form_valid(form)


class SubmissionFormView(LoginRequiredMixin, TemplateView):
    template_name = 'homework/forms/submit.html'
    # model = Submission
    # form_class = SubmissionForm
    # success_url = reverse_lazy('homework:homework_overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
            context['klass'] = klass
            definition = Definition.objects.get(pk=kwargs.get('definition_pk'))
            context['definition'] = definition
            context['student'] = klass.enrolled_students.get(user=self.request.user)
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        return context


class SubmissionEditFormView(LoginRequiredMixin, TemplateView):
    template_name = 'homework/forms/submit.html'

    # model = Submission
    # form_class = SubmissionForm
    # success_url = reverse_lazy('homework:homework_overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            klass = Klass.objects.get(pk=self.kwargs.get('klass_pk'))
            submission = Submission.objects.get(pk=self.kwargs.get('submission_pk'))
            context['submission'] = submission
            context['klass'] = klass
            definition = Definition.objects.get(pk=kwargs.get('definition_pk'))
            context['definition'] = definition
            context['student'] = klass.enrolled_students.get(user=self.request.user)
        except ObjectDoesNotExist:
            raise Http404('Klass object not found')
        return context


# class HomeworkOverView(LoginRequiredMixin, TemplateView):
#     template_name = 'homework/overview.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(HomeworkOverView, self).get_context_data(**kwargs)
#         try:
#             klass = Klass.objects.get(pk=kwargs.get('klass_pk'))
#             context['klass'] = klass
#         except ObjectDoesNotExist:
#             raise Http404('Klass object not found')
#         return context
