# Create your views here.

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

from apps.profiles.forms import InstructorProfileForm

# import pdb; pdb.set_trace()


def logout_view(request):
    #  TODO: Make confirmation that you want to logout?
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
        data = super(ChangePasswordView, self).get_form_kwargs(**kwargs)
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
        data = super(SetPasswordView, self).get_form_kwargs(**kwargs)
        data['user'] = self.request.user
        return data

    def form_valid(self, form):
        if self.request.user.has_set_password:
            raise Http404("You already have a usable password")
        else:
            self.request.user.set_password(form.cleaned_data.get('new_password1'))
            self.request.user.has_set_password = True
            self.request.user.save()
            return super().form_valid(form)


class InstructorProfileCreationView(LoginRequiredMixin, FormView):
    template_name = 'profiles/instructor_signup.html'
    form_class = InstructorProfileForm
    success_url = reverse_lazy('profiles:instructor_overview')

    def get_form_kwargs(self, **kwargs):
        data = super().get_form_kwargs(**kwargs)
        return data

    def form_valid(self, form):
        if not self.request.user.instructor:
            self.request.user.instructor = form.save()
            self.request.user.save()
        return super().form_valid(form)


class InstructorOverView(LoginRequiredMixin, TemplateView):
    template_name = 'instructor/overview.html'

    def dispatch(self, request, *args, **kwargs):
        # If the user doesn't have an instructor object, re-direct them to fill out the form first
        if request.user.is_authenticated and not self.request.user.instructor:
            return HttpResponseRedirect(reverse('profiles:instructor_signup'))
        else:
            return super().dispatch(request, *args, **kwargs)


class StudentOverView(LoginRequiredMixin, TemplateView):
    template_name = 'student/overview.html'


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/my_profile.html'
