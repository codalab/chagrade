from django import forms

from apps.profiles.models import Instructor
#
# class UserSetPasswordForm(forms.Form):
#     new_password = forms.PasswordInput(label='Password', max_length=100)
#     new_password_verify = forms.PasswordInput(label='Password', max_length=100)


class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['university_name']