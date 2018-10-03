# from django.shortcuts import render

# Create your views here.
# from django.views import View
# from django.views.generic import DetailView, TemplateView
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView

from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm

from apps.profiles.models import ChaUser


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
            self.request.user.has_set_password = True
            self.request.user.save()
            return super().form_valid(form)

# class LoginView
