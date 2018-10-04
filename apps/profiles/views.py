# from django.shortcuts import render

# Create your views here.
# from django.views import View
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

from apps.profiles.forms import InstructorProfileForm
from apps.profiles.models import ChaUser


import pdb; pdb.set_trace()


def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return redirect(reverse('index'))


class ChangePasswordView(LoginRequiredMixin, FormView):
    # model = ChaUser
    template_name = 'profiles/change_password.html'
    form_class = PasswordChangeForm
    success_url = 'index'

    def get_form_kwargs(self, **kwargs):
        # data = super(ChangePassword, self).get_form_kwargs(**kwargs)
        data = super(ChangePasswordView, self).get_form_kwargs()
        data['user'] = self.request.user
        return data

    def form_valid(self, form):
        return super().form_valid(form)


class SetPasswordView(LoginRequiredMixin, FormView):
    # model = ChaUser
    template_name = 'profiles/set_password.html'
    form_class = SetPasswordForm
    success_url = '/'

    def get_form_kwargs(self, **kwargs):
        # data = super(ChangePassword, self).get_form_kwargs(**kwargs)
        data = super(SetPasswordView, self).get_form_kwargs()
        data['user'] = self.request.user
        return data

    def form_valid(self, form):
        print(self.request.user.has_set_password)
        if self.request.user.has_set_password:
            print("Failed to set password, user has usable password")
            raise Http404("You already have a usable password")
        else:
            print("Password changed!")
            # print(form.cleaned_data)
            self.request.user.set_password(form.cleaned_data.get('new_password1'))
            self.request.user.has_set_password = True
            self.request.user.save()
            return super().form_valid(form)


class InstructorProfileCreationView(LoginRequiredMixin, FormView):
    template_name = 'profiles/instructor_signup.html'
    form_class = InstructorProfileForm
    success_url = reverse_lazy('profiles:instructor_overview')
    # success_url = '/profiles/instructor_overview/'

    def get_form_kwargs(self, **kwargs):
        data = super().get_form_kwargs()
        return data

    def form_valid(self, form):
        if not self.request.user.instructor:
            self.request.user.instructor = form.save()
            self.request.user.save()
            print("Instructor Profile created!")
        else:
            print("You already have an instructor profile!")
        return super().form_valid(form)


class InstructorOverView(LoginRequiredMixin, TemplateView):
    template_name = 'instructor_mgmt.html'

    def dispatch(self, request, *args, **kwargs):
        # If the user doesn't have an instructor object, re-direct them to fill out the form first
        if request.user.is_authenticated and not self.request.user.instructor:
            # return redirect(reverse('profiles:instructor_signup'))
            return HttpResponseRedirect(reverse('profiles:instructor_signup'))
        else:
            print("SEND USE")
            return super().dispatch(request, *args, **kwargs)

    # def get(self, request, *args, **kwargs):
    #     context = self.get_context_data(**kwargs)
    #     return render(request, template_name=self.template_name, context=context)
