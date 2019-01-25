from django import forms
from django.contrib.auth.forms import UsernameField, UserCreationForm
from django.forms import EmailField, CharField

from apps.profiles.models import Instructor, ChaUser


#
# class UserSetPasswordForm(forms.Form):
#     new_password = forms.PasswordInput(label='Password', max_length=100)
#     new_password_verify = forms.PasswordInput(label='Password', max_length=100)


class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['university_name']


class ChagradeCreationForm(UserCreationForm):
    class Meta:
        model = ChaUser
        fields = ("username", "email", "first_name", "last_name")
        field_classes = {
            'username': UsernameField,
            'email': EmailField,
            "first_name": CharField,
            "last_name": CharField
        }
