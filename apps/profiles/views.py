# Create your views here.

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

from apps.profiles.forms import InstructorProfileForm, ChagradeCreationForm, ChagradeUserLoginForm


def logout_view(request):
    #  TODO: Make confirmation that you want to logout?
    logout(request)
    # Redirect to a success page.
    return redirect(reverse('index'))


class ChangePasswordView(LoginRequiredMixin, FormView):
    # model = ChaUser
    template_name = 'profiles/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('index')

    def get_form_kwargs(self, **kwargs):
        data = super().get_form_kwargs(**kwargs)
        data['user'] = self.request.user
        return data

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data['new_password1'])
        self.request.user.save()
        user = authenticate(username=self.request.user.username, password=form.cleaned_data['new_password1'])
        login(self.request, user)
        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'profiles/login.html'
    form_class = ChagradeUserLoginForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
        login(self.request, user)
        return super().form_valid(form)


# class SetPasswordView(LoginRequiredMixin, FormView):
#     # model = ChaUser
#     template_name = 'profiles/set_password.html'
#     form_class = SetPasswordForm
#     success_url = '/'
#
#     def get_form_kwargs(self, **kwargs):
#         # data = super(ChangePassword, self).get_form_kwargs(**kwargs)
#         data = super(SetPasswordView, self).get_form_kwargs(**kwargs)
#         data['user'] = self.request.user
#         return data
#
#     def form_valid(self, form):
#         if self.request.user.has_set_password:
#             raise Http404("You already have a usable password")
#         else:
#             self.request.user.set_password(form.cleaned_data.get('new_password1'))
#             self.request.user.has_set_password = True
#             self.request.user.save()
#             return super().form_valid(form)


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


class SignUpView(FormView):
    template_name = 'profiles/sign_up.html'
    form_class = ChagradeCreationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        return super().form_valid(form)
